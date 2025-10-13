from __future__ import annotations

import logging
import uuid
from pathlib import Path

import click

from taskz.config import config_path, load_config
from taskz.db.connection import apply_migrations, connect
from taskz.expenses.exporters import export_csv
from taskz.expenses.importers import import_csv
from taskz.expenses.models import add_expense, add_rule, apply_rules, list_rules
from taskz.expenses.reports import merchant_summary, monthly_summary
from taskz.files.renamer import execute as execute_renames
from taskz.files.renamer import preview as preview_renames
from taskz.logging import setup_logging
from taskz.receipts.ingest import scrape_from_path
from taskz.utils.paths import iter_files, safe_rel

APP_DIR = Path.home() / ".task_automator"
MIGRATIONS_DIR = Path(__file__).parent / "db" / "migrations"


@click.group()
@click.option("--verbose", is_flag=True, help="Verbose logs")
@click.option("--quiet", is_flag=True, help="Reduce log output")
def cli(verbose: bool, quiet: bool):
    setup_logging(verbose=verbose, quiet=quiet)
    logging.getLogger(__name__).debug("CLI started")


@cli.group()
def db():
    """Database utilities."""
    pass


@db.command("init")
def db_init():
    """Create or migrate the SQLite database."""
    conn = connect()
    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    apply_migrations(conn, sql_files)
    click.echo(f"Database initialized at {APP_DIR}/taskz.db")


@db.command("stats")
def db_stats():
    conn = connect()
    n_exp = conn.execute("SELECT COUNT(*) c FROM expense").fetchone()["c"]
    n_rec = conn.execute("SELECT COUNT(*) c FROM receipt").fetchone()["c"]
    click.echo(f"expenses={n_exp} receipts={n_rec}")


@cli.group()
def config():
    """Show or edit config."""
    pass


@config.command("show")
def cfg_show():
    cfg = load_config()
    for k, v in cfg.items():
        click.echo(f"{k}: {v}")


@config.command("path")
def cfg_path():
    click.echo(str(config_path()))


@cli.group()
def files():
    """File operations."""
    pass


@files.command("rename")
@click.option(
    "--src",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
)
@click.option(
    "--dest",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
    help="Defaults to --src",
)
@click.option("--recursive/--no-recursive", default=True)
@click.option("--pattern", type=str, required=True)
@click.option("--lowercase", is_flag=True, help="Lowercase names")
@click.option("--dedupe", is_flag=True, help="Avoid name conflicts by suffixing -1,-2,...")
@click.option("--yes", is_flag=True, help="Apply changes (otherwise dry-run)")
def files_rename(
    src: Path,
    dest: Path | None,
    recursive: bool,
    pattern: str,
    lowercase: bool,
    dedupe: bool,
    yes: bool,
):
    """Preview and optionally execute bulk renames."""
    cfg = load_config()
    tz = cfg.get("timezone", "UTC")
    dest = dest or src
    previews = preview_renames(src, dest, pattern, recursive, tz, lowercase, dedupe)
    batch = uuid.uuid4().hex[:8]
    for it in previews:
        rel = safe_rel(src, it.src)
        click.echo(f"{rel} -> {it.dest.name}{'  [CONFLICT]' if it.conflict else ''}")
    changed = execute_renames(previews, yes=yes, batch_id=batch)
    if yes:
        click.echo(f"Executed batch {batch}: {changed} files")
    else:
        click.echo("Dry-run only. Use --yes to apply.")


@files.command("list")
@click.option(
    "--src",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
)
@click.option("--recursive/--no-recursive", default=True)
def files_list(src: Path, recursive: bool):
    for p in iter_files(src, recursive=recursive):
        click.echo(p)


@cli.group()
def receipts():
    """Receipt ingestion."""
    pass


@receipts.command("scrape")
@click.option(
    "--from",
    "from_path",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
)
@click.option("--globs", type=str, default="*.html,*.json", help="Comma-separated glob patterns")
@click.option(
    "--vendor",
    type=click.Choice(["auto", "generic_html", "jumia", "uber"]),
    default="auto",
)
@click.option("--yes", is_flag=True, help="Confirm ingestion")
def receipts_scrape(from_path: Path, globs: str, vendor: str, yes: bool):
    if not yes:
        click.echo("Dry-run: add --yes to ingest")
        return
    patterns = [g.strip() for g in globs.split(",") if g.strip()]
    n = scrape_from_path(from_path, patterns, vendor=vendor)
    click.echo(f"Ingested {n} receipts")


@cli.group()
def expenses():
    """Expense management."""
    pass


@expenses.command("add")
@click.option("--date", required=True)
@click.option("--merchant", required=True)
@click.option("--amount", type=float, required=True)
@click.option("--currency", required=True)
@click.option("--category", default=None)
@click.option("--description", default=None)
@click.option("--tax", type=float, default=None)
@click.option("--tags", "tags_csv", default=None)
def exp_add(date, merchant, amount, currency, category, description, tax, tags_csv):
    rid = add_expense(date, merchant, amount, currency, category, description, tax, tags_csv)
    click.echo(f"Expense id={rid} added")


@expenses.group("rules")
def exp_rules():
    """Rules for auto-categorization."""
    pass


@exp_rules.command("add")
@click.option("--field", "target_field", required=True, type=click.Choice(["category"]))
@click.option("--pattern", required=True, help="Substring match for MVP")
@click.option("--value", required=True)
@click.option("--priority", type=int, default=100)
@click.option("--enabled/--disabled", default=True)
def rule_add(target_field, pattern, value, priority, enabled):
    add_rule(target_field, pattern, value, priority, enabled)
    click.echo("Rule added")


@exp_rules.command("list")
def rule_list():
    for r in list_rules():
        click.echo(
            f"[{r['id']}] {r['enabled']} prio={r['priority']} "
            f"if ~{r['pattern']} => set {r['target_field']}={r['value']}"
        )


@exp_rules.command("apply")
def rule_apply():
    n = apply_rules()
    click.echo(f"Updated {n} expenses")


@expenses.group("report")
def exp_report():
    """Reports and summaries."""
    pass


@exp_report.command("monthly")
@click.option("--since", required=True)
@click.option("--until", required=True)
def report_monthly(since, until):
    rows = monthly_summary(since, until)
    click.echo("Month     Category         Total")
    click.echo("--------------------------------")
    for r in rows:
        click.echo(f"{r['month']:<9} {str(r['category'] or '-'): <15} {r['total']:.2f}")


@exp_report.command("merchant")
@click.option("--since", required=True)
@click.option("--until", required=True)
def report_merchant(since, until):
    rows = merchant_summary(since, until)
    click.echo("Merchant                     Total")
    click.echo("----------------------------------")
    for r in rows:
        click.echo(f"{r['merchant']:<28} {r['total']:.2f}")


@expenses.command("import")
@click.option(
    "--csv",
    "csv_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
)
@click.option("--currency-default", default="KES")
def exp_import(csv_path: Path, currency_default: str):
    n = import_csv(csv_path, currency_default)
    click.echo(f"Imported {n} expenses")


@expenses.command("export")
@click.option(
    "--csv",
    "csv_path",
    type=click.Path(path_type=Path, dir_okay=False),
    required=True,
)
@click.option("--since", default=None)
@click.option("--until", default=None)
@click.option("--category", default=None)
def exp_export(csv_path: Path, since: str | None, until: str | None, category: str | None):
    n = export_csv(csv_path, since=since, until=until, category=category)
    click.echo(f"Exported {n} rows to {csv_path}")


def main():
    cli()


if __name__ == "__main__":
    main()