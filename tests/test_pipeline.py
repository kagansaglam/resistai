"""Network-free tests for the ResistAI pipeline scripts and stored results."""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script, args, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        cwd=cwd, capture_output=True, text=True,
    )


def write_pocket_json(path, uid, total, high, med, low, best, best_id="1", skipped=False):
    path.write_text(json.dumps({
        "uniprot_id": uid,
        "total_pockets": total,
        "skipped": skipped,
        "summary": {
            "high_druggability": high,
            "medium_druggability": med,
            "low_druggability": low,
            "best_score": best,
            "best_pocket_id": best_id,
        },
        "all_pockets": [],
    }))


# --- find_pockets.py -------------------------------------------------------

def test_find_pockets_skips_placeholder_structure(tmp_path):
    pdb = tmp_path / "X.pdb"
    pdb.write_text("PLACEHOLDER structure")
    result = run("find_pockets.py", ["P12345", pdb], tmp_path)
    assert result.returncode == 0, result.stderr
    out = json.loads((tmp_path / "P12345_pockets.json").read_text())
    assert out["skipped"] is True
    assert out["total_pockets"] == 0
    assert out["summary"]["best_score"] is None


# --- summary_report.py -----------------------------------------------------

def test_summary_report_ranks_proteins_by_best_score(tmp_path):
    a, b = tmp_path / "A_pockets.json", tmp_path / "B_pockets.json"
    write_pocket_json(a, "A", 5, 0, 1, 4, 0.427)
    write_pocket_json(b, "B", 6, 1, 0, 5, 0.755)
    out_csv = tmp_path / "summary.csv"
    result = run("summary_report.py",
                 [a, b, "--proteins", tmp_path / "none.json", "--output", out_csv], tmp_path)
    assert result.returncode == 0, result.stderr
    rows = list(csv.DictReader(out_csv.open()))
    assert [r["uniprot_id"] for r in rows] == ["B", "A"]  # highest score first
    assert float(rows[0]["best_score"]) == 0.755


def test_summary_report_ignores_skipped_and_scoreless_entries(tmp_path):
    ok, skipped, none = (tmp_path / f"{n}_pockets.json" for n in ("OK", "SK", "NO"))
    write_pocket_json(ok, "OK", 3, 0, 0, 3, 0.2)
    write_pocket_json(skipped, "SK", 0, 0, 0, 0, None, skipped=True)
    write_pocket_json(none, "NO", 0, 0, 0, 0, None)
    out_csv = tmp_path / "summary.csv"
    result = run("summary_report.py",
                 [ok, skipped, none, "--proteins", tmp_path / "none.json", "--output", out_csv],
                 tmp_path)
    assert result.returncode == 0, result.stderr
    rows = list(csv.DictReader(out_csv.open()))
    assert [r["uniprot_id"] for r in rows] == ["OK"]


# --- tier definition -------------------------------------------------------

@pytest.mark.parametrize("score,expected", [
    (1.0, "high"), (0.7, "high"), (0.699, "medium"),
    (0.4, "medium"), (0.399, "low"), (0.0, "low"),
])
def test_tier_thresholds(score, expected):
    sys.path.insert(0, str(SCRIPTS))
    from reproduce_paper_stats import tier
    assert tier(score) == expected


# --- stored results --------------------------------------------------------

@pytest.mark.parametrize("name", ["proteins_annotated.csv", "proteins_annotated_full.csv"])
def test_results_tables_are_consistent(name):
    rows = list(csv.DictReader((ROOT / "results" / name).open()))
    assert rows, "results table is empty"
    ids = [r["uniprot_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate UniProt identifiers"
    for r in rows:
        assert 0.0 <= float(r["best_score"]) <= 1.0
        assert int(r["total_pockets"]) == (
            int(r["high_druggability"]) + int(r["medium_druggability"]) + int(r["low_druggability"])
        )


def test_classifier_metrics_file_is_sane():
    m = json.loads((ROOT / "models" / "classifier_metrics.json").read_text())
    assert m["n_train"] + m["n_test"] == 2433
    assert set(m["classes"]) == {"high", "medium", "low"}
    assert 0.5 < m["test_roc_auc_ovr_weighted"] < 1.0
    assert 0.0 < m["test_accuracy"] <= 1.0
