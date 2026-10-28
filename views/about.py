import streamlit as st
from pathlib import Path

from ui.navigation import build_pages, render_navigation
from ui.runtime import ROOT, load_engine


engine = load_engine()
render_navigation(build_pages(Path(ROOT)), "Tentang aplikasi")
st.markdown(
    '<section class="hf-page-ribbon"><h1>Tentang aplikasi</h1>'
    '<p>Informasi sumber, cakupan, dan batasan HuntFacts.</p></section>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="hf-info hf-info-first">
      <h2>HuntFacts</h2>
      <p>HuntFacts membantu menemukan artikel klarifikasi yang terkait dengan
      pesan berantai. Sistem tidak menentukan kesimpulan untuk pesanmu.</p>
      <h2>Sumber data</h2>
      <p>Koleksi berisi {len(engine.docs):,} artikel dari turnbackhoax.id.
      Data diambil sampai 25 April 2021 dan berasal dari repositori
      JibranFawaid/turnbackhoax-dataset.</p>
      <h2>Batasan</h2>
      <p>Hasil pencarian menunjukkan kemiripan teks, bukan keputusan tentang
      isi pesan. Koleksi tidak mencakup artikel setelah April 2021.</p>
      <h2>Status data</h2>
      <p>Status lisensi dataset belum jelas. Periksa ketentuan sumber asli
      sebelum menyebarluaskan data.</p>
    </section>
    """.replace(",", "."),
    unsafe_allow_html=True,
)
