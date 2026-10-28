from scripts import demo


def test_demo_runs_and_verifies(tmp_path, capsys):
    assert demo.main(["--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "M(p, q) = 61/75" in out
    assert "28/28 checks passed" in out
    assert out.rstrip().endswith("VERDICT: PASS")
    assert (tmp_path / "p2_5-q3_5.json").exists()


def test_demo_outside_scope_point(tmp_path, capsys):
    assert demo.main(["--p", "3/5", "--q", "2/5", "--out", str(tmp_path)]) == 0
    assert "M(p, q) = 19/25" in capsys.readouterr().out
