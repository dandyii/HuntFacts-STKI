from pathlib import Path

import pandas as pd
import pytest

from huntfacts_core import HuntFactsEngine


ROOT = Path(__file__).resolve().parents[1]
QUERY = (
    "info dr grup sebelah, lg dicari relawan nakes utk rawat pasien covid "
    "di wisma atlet jakarta, gajinya 6 jutaan dpt mes, kontak dr irna. "
    "tolong dishare ya"
)


@pytest.fixture(scope="module")
def engine():
    docs = pd.read_csv(ROOT / "artifacts" / "docs_clean.csv").fillna("")
    return HuntFactsEngine.from_docs(docs, chain_stop=True, slang_norm=True)


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("bm25", [(634, 93.85), (2765, 73.80), (848, 68.70)]),
        ("tfidf", [(634, 0.5445), (2765, 0.3952), (848, 0.3632)]),
    ],
)
def test_golden_query_ranking(engine, method, expected):
    _, rows = engine.search(
        QUERY,
        method=method,
        weights=(1.0, 0.0),
        top_k=3,
    )

    assert [row["doc_id"] for row in rows] == [doc_id for doc_id, _ in expected]
    assert [row["score"] for row in rows] == pytest.approx(
        [score for _, score in expected],
        abs=0.01,
    )
