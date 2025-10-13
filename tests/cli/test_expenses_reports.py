from click.testing import CliRunner
from taskz.cli import cli

def test_expense_rules_and_reports():
    runner = CliRunner()
    # add expenses
    e1 = runner.invoke(
        cli,
        ["expenses", "add", "--date", "2025-10-12", "--merchant", "Uber", "--amount", "450", "--currency", "KES"],
    )
    assert e1.exit_code == 0
    e2 = runner.invoke(
        cli,
        ["expenses", "add", "--date", "2025-10-13", "--merchant", "Jumia", "--amount", "999", "--currency", "KES"],
    )
    assert e2.exit_code == 0

    # add rule: merchant contains 'Uber' -> category Transport
    r = runner.invoke(cli, ["expenses", "rules", "add", "--field", "category", "--pattern", "Uber", "--value", "Transport"])
    assert r.exit_code == 0
    ap = runner.invoke(cli, ["expenses", "rules", "apply"])
    assert ap.exit_code == 0

    # monthly report
    rep = runner.invoke(cli, ["expenses", "report", "monthly", "--since", "2025-01-01", "--until", "2025-12-31"])
    assert rep.exit_code == 0
    assert "Month" in rep.output
    # merchant report
    mr = runner.invoke(cli, ["expenses", "report", "merchant", "--since", "2025-01-01", "--until", "2025-12-31"])
    assert mr.exit_code == 0
    assert "Uber" in mr.output
