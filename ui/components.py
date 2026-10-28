import html
from typing import Any
from urllib.parse import urlparse

import streamlit as st


MONTHS = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)
ALLOWED_HOST = "turnbackhoax.id"


def _safe_link(link: Any) -> str | None:
    parsed = urlparse(str(link))
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        return None
    return str(link)


def _date_label(value: Any) -> str:
    text = str(value or "").strip()
    parts = text[:10].split("-")
    if len(parts) != 3:
        return "Tanggal tidak tersedia"
    try:
        return f"{int(parts[2])} {MONTHS[int(parts[1]) - 1]} {parts[0]}"
    except (ValueError, IndexError):
        return "Tanggal tidak tersedia"


def render_hero() -> None:
    st.markdown(
        """
        <section class="hf-hero" id="beranda">
          <p class="hf-kicker">Telusuri klarifikasi sebelum dibagikan</p>
          <h1>Dapat pesan berantai?<br><span>Cek dulu sebelum dibagikan.</span></h1>
          <p>Tempel pesannya di sini. HuntFacts mencarikan artikel klarifikasi
          yang mirip dari turnbackhoax.id.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _choose_example(example: str) -> None:
    st.session_state.pending_query = example
    st.session_state.search_result = None


def render_examples(examples: list[str]) -> None:
    st.markdown('<p class="hf-example-label">Coba contoh pesan</p>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, example in zip(columns, examples):
        with column:
            st.button(
                example,
                key=f"example_{examples.index(example)}",
                use_container_width=True,
                on_click=_choose_example,
                args=(example,),
            )


def render_disclaimer() -> None:
    st.markdown(
        '<p class="hf-disclaimer">HuntFacts hanya menemukan klarifikasi yang terkait. '
        'Benar atau salahnya pesan tetap kamu simpulkan dari artikel aslinya.</p>',
        unsafe_allow_html=True,
    )


def render_message_preview(engine: Any, query: str, terms: list[str]) -> None:
    preview = query[:600]
    truncated = len(query) > 600
    st.markdown('<h2 class="hf-section-title">Pesanmu</h2>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hf-message-preview">{engine.highlight(preview, terms)}</div>',
        unsafe_allow_html=True,
    )
    if truncated:
        with st.expander("Tampilkan seluruh pesan"):
            st.markdown(
                f'<div class="hf-message-preview">{engine.highlight(query, terms)}</div>',
                unsafe_allow_html=True,
            )


def render_results(rows: list[dict[str, Any]], docs: Any) -> None:
    if not rows:
        st.markdown(
            '<section class="hf-empty"><h2>Belum ada klarifikasi yang cocok</h2>'
            '<p>Ini tidak berarti pesannya benar. Koleksi hanya mencakup artikel sampai '
            'April 2021. Coba tempel bagian intinya saja.</p></section>',
            unsafe_allow_html=True,
        )
        return

    max_score = max(row["score"] for row in rows) or 1
    st.markdown(
        f'<h2 class="hf-section-title">Ditemukan {len(rows)} klarifikasi yang mirip</h2>',
        unsafe_allow_html=True,
    )
    for number, row in enumerate(rows, 1):
        link = _safe_link(row["link"])
        if not link:
            continue
        doc = docs.loc[docs["doc_id"] == row["doc_id"]].iloc[0]
        tag = str(doc.get("tag", "")).strip()
        label = (
            f'<span class="hf-badge">Label turnbackhoax.id: {html.escape(tag)}</span>'
            if tag else ""
        )
        relative = max(0.0, min(100.0, row["score"] / max_score * 100))
        st.markdown(
            f"""
            <article class="hf-result">
              <div class="hf-result-title">
                <span class="hf-result-number">{number}</span>
                <a href="{html.escape(link, quote=True)}" target="_blank"
                   rel="noopener noreferrer">{row['title_html']}</a>
              </div>
              <div class="hf-meta"><span>{_date_label(doc.get('date', ''))}</span>{label}</div>
              <div class="hf-similarity" role="img"
                   aria-label="Kemiripan relatif terhadap hasil teratas">
                <span style="width:{relative:.2f}%"></span>
              </div>
              <div class="hf-snippet">{row['snippet_html']}</div>
              <a class="hf-source-link" href="{html.escape(link, quote=True)}"
                 target="_blank" rel="noopener noreferrer">
                Baca artikel asli di turnbackhoax.id
              </a>
              <div class="hf-future-space" aria-hidden="true"></div>
            </article>
            """,
            unsafe_allow_html=True,
        )


def render_technical_details(terms: list[str], method: str, rows: list[dict[str, Any]], elapsed: float) -> None:
    with st.expander("Detail teknis"):
        st.markdown(
            f"""
            <div class="hf-technical">
              <p><b>Kata kunci:</b> {html.escape(", ".join(terms) or "(tidak ada)")}</p>
              <p><b>Metode:</b> {html.escape(method)}</p>
              <p><b>Skor mentah:</b> {html.escape(", ".join(f"{r['score']:.3f}" for r in rows) or "(tidak ada)")}</p>
              <p><b>Waktu pencarian:</b> {elapsed * 1000:.1f} ms</p>
              <p>Bar kemiripan bersifat relatif terhadap hasil teratas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_home_preview(engine: Any, query: str, rows: list[dict[str, Any]]) -> None:
    max_score = max((row["score"] for row in rows), default=0) or 1
    result_lines = []
    for row in rows[:3]:
        relative = max(0.0, min(100.0, row["score"] / max_score * 100))
        title = html.escape(str(row["title"]))
        matching_docs = engine.docs.loc[engine.docs["doc_id"] == row["doc_id"]]
        date = _date_label(matching_docs.iloc[0].get("date", "")) if not matching_docs.empty else "Tanggal tidak tersedia"
        result_lines.append(
            f'<div class="hf-preview-result"><span>{title}</span><small>{date}</small>'
            f'<span class="hf-preview-bar"><i style="width:{relative:.2f}%"></i></span></div>'
        )
    st.markdown(
        f"""
        <div class="hf-home-preview">
          <p class="hf-preview-title">Contoh pencarian</p>
          <p class="hf-preview-query">{html.escape(query)}</p>
          {''.join(result_lines) or '<p class="hf-preview-empty">Belum ada hasil terkait.</p>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_sections() -> None:
    st.markdown(
        """
        <section class="hf-info" id="cara-kerja">
          <h2>Cara kerja</h2>
          <p>HuntFacts membersihkan pesan, mengubah kata ke bentuk dasar,
          mencari kata pada indeks artikel, lalu mengurutkan artikel yang terkait.</p>
          <ol>
            <li>Pembersihan teks dan penghapusan kata umum</li>
            <li>Stemming untuk menyamakan bentuk kata</li>
            <li>Pencarian pada indeks isi dan judul</li>
            <li>Peringkat dengan BM25 atau TF-IDF</li>
          </ol>
        </section>
        <section class="hf-info" id="tentang">
          <h2>Tentang HuntFacts</h2>
          <p>Koleksi bersumber dari turnbackhoax.id dan repositori
          JibranFawaid/turnbackhoax-dataset. Cakupan artikel sampai April 2021.
          Status lisensi dataset belum jelas.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
