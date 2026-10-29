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


def test_saved_demo_output_is_current(tmp_path, capsys):
    """results/demo_output.txt matches the demo, except platform-dependent float lines."""
    from conftest import REPO

    def stable(text):
        return [line for line in text.splitlines()
                if "HiGHS" not in line and "certificate:" not in line]

    assert demo.main(["--out", str(tmp_path)]) == 0
    current = capsys.readouterr().out
    saved = (REPO / "results" / "demo_output.txt").read_text(encoding="utf-8")
    assert stable(current) == stable(saved)
