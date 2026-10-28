import time
from pathlib import Path

import streamlit as st

from ui.components import (
    render_disclaimer,
    render_examples,
    render_message_preview,
    render_results,
    render_technical_details,
)
from ui.navigation import build_pages, render_navigation
from ui.runtime import EXAMPLES, ROOT, load_engine


engine = load_engine()
docs = engine.docs
render_navigation(build_pages(Path(ROOT)), "Cari klarifikasi")

st.markdown(
    '<section class="hf-page-ribbon"><h1>Cari klarifikasi</h1>'
    '<p>Temukan artikel yang terkait dengan pesan yang kamu terima.</p></section>',
    unsafe_allow_html=True,
)

if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "pending_query" in st.session_state:
    st.session_state.query_text = st.session_state.pop("pending_query")

render_examples(EXAMPLES)
query = st.text_area(
    "Tempel pesan berantai atau klaim yang ingin dicari",
    key="query_text",
    height=220,
    max_chars=5000,
    placeholder="Tempel pesan berantai atau klaim di sini",
)
search_col, clear_col = st.columns([2, 1])
with search_col:
    search_clicked = st.button("Cari klarifikasi", type="primary", use_container_width=True)


def clear_search() -> None:
    st.session_state.query_text = ""
    st.session_state.search_result = None


with clear_col:
    st.button("Bersihkan", use_container_width=True, on_click=clear_search, key="clear_search_button")

render_disclaimer()
with st.expander("Pengaturan lanjutan"):
    method_label = st.radio("Metode ranking", ["BM25", "TF-IDF + Cosine"], index=0)
    method = "bm25" if method_label == "BM25" else "tfidf"
    top_k = st.slider("Jumlah hasil", 5, 10, 10)
    w_title = st.slider(
        "Bobot judul", 0.0, 3.0, 0.0, 0.5,
        help="0 berarti hanya isi artikel yang dipakai. Makin besar, makin penting kecocokan di judul.",
    )
    use_reduce = st.checkbox(
        "Ringkas pesan panjang ke kata kunci penting", value=False,
        help="Sistem memilih kata dengan bobot IDF tertinggi dari pesanmu.",
    )
    reduce_k = st.slider("Jumlah kata kunci", 3, 30, 10) if use_reduce else None

if search_clicked:
    if not query.strip():
        st.warning("Tempel dulu pesan yang ingin dicari.")
    elif len(query) > 5000:
        st.warning("Pesan terlalu panjang. Maksimal 5.000 karakter. Persingkat lalu coba lagi.")
    else:
        started = time.perf_counter()
        article_count = f"{len(engine.docs):,}".replace(",", ".")
        with st.spinner(f"Mencari di {article_count} artikel klarifikasi"):
            terms, rows = engine.search(
                query, method=method, top_k=top_k, weights=(1.0, w_title), reduce_k=reduce_k
            )
        st.session_state.search_result = {
            "query": query, "terms": terms, "rows": rows,
            "method": method_label, "elapsed": time.perf_counter() - started,
        }

result = st.session_state.search_result
if result:
    render_message_preview(engine, result["query"], result["terms"])
    render_results(result["rows"], docs)
    render_technical_details(result["terms"], result["method"], result["rows"], result["elapsed"])
