import os

import pandas as pd
import streamlit as st

from huntfacts_core import HuntFactsEngine

st.set_page_config(page_title="HuntFacts", page_icon="🔎", layout="wide")

ENGINE_PATH = "artifacts/engine_full.pkl"
DOCS_PATH = "artifacts/docs_clean.csv"


@st.cache_resource(show_spinner="Memuat indeks klarifikasi, mohon tunggu sebentar...")
def load_engine():
    if os.path.exists(ENGINE_PATH):
        return HuntFactsEngine.load(ENGINE_PATH)
    docs = pd.read_csv(DOCS_PATH).fillna("")
    return HuntFactsEngine.from_docs(docs, chain_stop=True, slang_norm=True)


st.markdown(
    """
    <style>
    .hf-card {border:1px solid rgba(128,128,128,.35); border-radius:10px;
              padding:12px 16px; margin:10px 0;}
    .hf-score {color:#888; font-size:0.85em;}
    .hf-snippet {font-size:0.92em; margin-top:6px; line-height:1.5;}
    mark {background:#ffe066; color:#000; padding:0 2px; border-radius:3px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔎 HuntFacts")
st.caption("Sistem temu kembali klarifikasi hoaks berbahasa Indonesia untuk pesan berantai (TF-IDF dan BM25)")
st.info(
    "HuntFacts hanya menampilkan artikel klarifikasi yang **terkait** dengan pesan yang kamu tempel. "
    "Sistem ini tidak menentukan pesan tersebut benar atau salah. "
    "Selalu baca artikel aslinya di turnbackhoax.id untuk kesimpulan lengkap."
)

engine = load_engine()

with st.sidebar:
    st.header("Pengaturan")
    method_label = st.radio("Metode ranking", ["BM25", "TF-IDF + Cosine"], index=0)
    method = "bm25" if method_label == "BM25" else "tfidf"
    top_k = st.slider("Jumlah hasil", 5, 10, 10)
    w_title = st.slider("Bobot judul", 0.0, 3.0, 0.0, 0.5,
                        help="0 berarti hanya isi artikel yang dipakai. Makin besar, makin penting kecocokan di judul.")
    use_reduce = st.checkbox("Ringkas pesan panjang ke kata kunci penting", value=False,
                             help="Sistem memilih kata dengan bobot IDF tertinggi dari pesanmu.")
    reduce_k = st.slider("Jumlah kata kunci", 3, 30, 10) if use_reduce else None
    st.caption(f"Koleksi: {len(engine.docs):,} artikel klarifikasi")

query = st.text_area(
    "Tempel pesan berantai atau klaim yang ingin dicek",
    height=220,
    placeholder="Contoh: Heboh! Minum air rebusan daun sirsak bisa sembuhkan kanker dalam 3 hari, sebarkan ke 10 grup!",
)

if st.button("Cari klarifikasi terkait", type="primary"):
    if not query.strip():
        st.warning("Tempel dulu pesan yang ingin dicek.")
    else:
        qterms, rows = engine.search(
            query, method=method, top_k=top_k, weights=(1.0, w_title), reduce_k=reduce_k
        )
        st.markdown("**Kata kunci yang dipakai sistem:** " + (", ".join(qterms) if qterms else "(tidak ada)"))
        if not rows:
            st.warning("Belum ada klarifikasi yang cocok dengan pesan ini di koleksi. "
                       "Ini tidak berarti pesannya benar. Koleksi hanya mencakup artikel sampai waktu scraping.")
        for i, r in enumerate(rows, 1):
            st.markdown(
                f"""
                <div class="hf-card">
                  <b>{i}. <a href="{r['link']}" target="_blank">{r['title_html']}</a></b>
                  <span class="hf-score"> &nbsp; skor {r['score']:.3f}</span>
                  <div class="hf-snippet">{r['snippet_html']}</div>
                  <div class="hf-score" style="margin-top:6px">Sumber: <a href="{r['link']}" target="_blank">{r['link']}</a></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
