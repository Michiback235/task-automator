from pathlib import Path
from click.testing import CliRunner
from taskz.cli import cli

def test_files_rename_preview_and_execute(sample_files, monkeypatch):
    runner = CliRunner()
    # preview (no --yes)
    res = runner.invoke(
        cli,
        ["files", "rename", "--src", str(sample_files), "--pattern", "{name}.{ext}"],
    )
    assert res.exit_code == 0
    assert "Dry-run only." in res.output

    # execute
    res2 = runner.invoke(
        cli,
        ["files", "rename", "--src", str(sample_files), "--pattern", "{created:%Y-%m-%d}_{name}.{ext}", "--yes"],
    )
    assert res2.exit_code == 0
    assert "Executed batch" in res2.output
