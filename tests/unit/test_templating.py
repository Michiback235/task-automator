from taskz.files.renamer import render_pattern

def test_render_basic(tmp_path):
    p = tmp_path / "X.txt"
    p.write_text("x")
    out = render_pattern(p, "{name}.{ext}", "UTC")
    assert out == "X.txt"
    out2 = render_pattern(p, "{parent}_{name}.{ext}", "UTC")
    assert out2.endswith("X.txt")  # parent depends on tmp path name
