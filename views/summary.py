import streamlit as st
from pathlib import Path

from ui.navigation import build_pages, render_navigation
from ui.runtime import ROOT, load_engine


engine = load_engine()
docs = engine.docs
render_navigation(build_pages(Path(ROOT)), "Ringkasan")
st.markdown(
    '<section class="hf-page-ribbon"><h1>Ringkasan koleksi</h1>'
    '<p>Gambaran yang dihitung langsung dari artikel yang tersedia.</p></section>',
    unsafe_allow_html=True,
)

st.markdown('<div class="hf-stat-grid">', unsafe_allow_html=True)
cols = st.columns(4)
stats = [
    ("Jumlah artikel", f"{len(docs):,}".replace(",", ".")),
    ("Ukuran kosakata", f"{engine.content.vocab_size:,}".replace(",", ".")),
    ("Artikel berlabel", f"{docs['tag'].astype(str).str.strip().ne('').sum():,}".replace(",", ".")),
    ("Rentang tanggal", f"{docs['date'].min()} sampai {docs['date'].max()}"),
]
for col, (label, value) in zip(cols, stats):
    with col:
        st.markdown(f'<div class="hf-stat"><strong>{value}</strong><span>{label}</span></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<h2 class="hf-section-title">Label sumber</h2>', unsafe_allow_html=True)
labels = docs["tag"].astype(str).str.strip().replace("", "Tanpa label").value_counts().rename_axis("Label").reset_index(name="Jumlah")
labels["Jumlah"] = labels["Jumlah"].map(lambda value: f"{value:,}".replace(",", "."))
st.dataframe(labels, use_container_width=True, hide_index=True)
