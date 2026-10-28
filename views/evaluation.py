import streamlit as st
from pathlib import Path

from ui.navigation import build_pages, render_navigation
from ui.runtime import ROOT, load_evaluation_file


render_navigation(build_pages(Path(ROOT)), "Evaluasi")
st.markdown(
    '<section class="hf-page-ribbon"><h1>Evaluasi</h1>'
    '<p>Hasil penilaian relevansi dari berkas evaluasi yang tersedia.</p></section>',
    unsafe_allow_html=True,
)

pool = load_evaluation_file("pool_for_annotation.csv")
annotator_a = load_evaluation_file("annotator_A.csv")
annotator_b = load_evaluation_file("annotator_B.csv")

if pool is None:
    st.info("Berkas evaluasi belum tersedia.")
else:
    st.markdown('<h2 class="hf-section-title">Kumpulan penilaian</h2>', unsafe_allow_html=True)
    st.metric("Baris penilaian", f"{len(pool):,}".replace(",", "."))
    if "relevan" not in pool or pool["relevan"].astype(str).str.strip().eq("").all():
        st.info("Kolom relevan belum diisi. Belum ada angka evaluasi yang dapat ditampilkan.")
    else:
        values = pool["relevan"].astype(str).str.strip()
        values = values[values.isin(["0", "1"])]
        if values.empty:
            st.info("Belum ada penilaian relevansi yang dapat dihitung.")
        else:
            st.dataframe(
                values.value_counts().rename_axis("Nilai").reset_index(name="Jumlah"),
                use_container_width=True, hide_index=True,
            )

if annotator_a is None or annotator_b is None:
    st.info("Cohen's kappa belum ditampilkan karena kedua berkas annotator belum tersedia.")
else:
    st.info("Berkas kedua annotator tersedia, tetapi perhitungan kappa belum dilakukan oleh notebook.")
