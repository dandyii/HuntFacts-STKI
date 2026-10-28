import streamlit as st
from pathlib import Path

from ui.components import render_home_preview
from ui.navigation import build_pages, render_navigation
from ui.runtime import EXAMPLES, ROOT, load_engine


engine = load_engine()
render_navigation(build_pages(Path(ROOT)), "Beranda")
preview_query = EXAMPLES[1]
_, preview_rows = engine.search(preview_query, method="bm25", top_k=3, weights=(1.0, 0.0))

st.markdown(
    """
    <section class="hf-home-hero">
      <div>
        <p class="hf-kicker">Telusuri klarifikasi sebelum dibagikan</p>
        <h1>Mulai dari pesan yang kamu terima.</h1>
        <p>Tempel klaim atau pesan berantai untuk menemukan artikel klarifikasi
        yang terkait dari turnbackhoax.id.</p>
        <div class="hf-home-actions">
          <a class="hf-action-link" href="/cari">Coba sekarang</a>
          <a class="hf-quiet-link" href="/evaluasi">Lihat evaluasi</a>
        </div>
      </div>
    </section>
    <section class="hf-chip-row">
      <span class="hf-chip">6.969 artikel dalam koleksi</span>
      <span class="hf-chip">BM25 dan TF-IDF</span>
      <span class="hf-chip">Sumber turnbackhoax.id</span>
    </section>
    """,
    unsafe_allow_html=True,
)
render_home_preview(engine, preview_query, preview_rows)

st.markdown('<h2 class="hf-section-title">Cara mulai</h2>', unsafe_allow_html=True)
cols = st.columns(3)
steps = [
    ("1", "Tempel pesan", "Masukkan bagian pesan yang ingin kamu cari."),
    ("2", "Baca hasil terkait", "Periksa judul, tanggal, label sumber, dan isi artikel."),
    ("3", "Simpulkan sendiri", "Baca artikel asli sebelum mengambil keputusan."),
]
for col, (number, title, text) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="hf-step"><span>{number}</span><h3>{title}</h3><p>{text}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<p class="hf-disclaimer">HuntFacts hanya menemukan klarifikasi yang terkait. '
    'Benar atau salahnya pesan tetap kamu simpulkan dari artikel aslinya.</p>',
    unsafe_allow_html=True,
)
