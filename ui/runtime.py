import os

import pandas as pd
import streamlit as st

from huntfacts_core import HuntFactsEngine


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_PATH = os.path.join(ROOT, "artifacts", "engine_full.pkl")
DOCS_PATH = os.path.join(ROOT, "artifacts", "docs_clean.csv")
EVAL_PATH = os.path.join(ROOT, "data", "eval")
EXAMPLES = [
    "Pesan berantai menyebut air rebusan tanaman tertentu bisa menyembuhkan semua penyakit.",
    "Ada kabar bantuan tunai baru yang meminta warga mengisi formulir melalui sebuah tautan.",
    "Pesan menyebut sebuah produk rumah tangga dapat mencegah penularan penyakit.",
]


@st.cache_resource(show_spinner="Memuat indeks klarifikasi, mohon tunggu sebentar...")
def load_engine():
    if os.path.exists(ENGINE_PATH):
        return HuntFactsEngine.load(ENGINE_PATH)
    docs = pd.read_csv(DOCS_PATH).fillna("")
    return HuntFactsEngine.from_docs(docs, chain_stop=True, slang_norm=True)


def load_evaluation_file(name: str) -> pd.DataFrame | None:
    path = os.path.join(EVAL_PATH, name)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path).fillna("")
