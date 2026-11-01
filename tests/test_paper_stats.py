"""The numbers reported in the manuscript must be reproducible from the stored results table."""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from reproduce_paper_stats import compute_stats  # noqa: E402


@pytest.fixture(scope="module")
def result():
    return compute_stats(pd.read_csv(ROOT / "results" / "proteins_annotated_full.csv"))


def test_dataset_size_and_pockets(result):
    assert result["n_proteins"] == 2433
    assert result["total_pockets"] == 63937


def test_tier_counts(result):
    assert result["tiers"] == {"high": 1198, "medium": 717, "low": 518}


def test_score_distribution(result):
    assert result["mean_score"] == pytest.approx(0.643, abs=1e-3)
    assert result["sd_score"] == pytest.approx(0.264, abs=1e-3)


def test_family_anova(result):
    assert result["n_labelled_proteins"] == 118
    assert result["anova_F"] == pytest.approx(3.875, abs=1e-3)
    assert result["anova_p"] == pytest.approx(0.0032, abs=1e-4)
    efflux = result["family_table"]["efflux pump"]
    assert efflux["count"] == 23
    assert efflux["mean"] == pytest.approx(0.785, abs=1e-3)
