from pathlib import Path

import streamlit as st


def build_pages(root: Path) -> list[st.Page]:
    return [
        st.Page(str(root / "views" / "home.py"), title="Beranda", url_path="", default=True),
        st.Page(str(root / "views" / "search.py"), title="Cari klarifikasi", url_path="cari"),
        st.Page(str(root / "views" / "evaluation.py"), title="Evaluasi", url_path="evaluasi"),
        st.Page(str(root / "views" / "summary.py"), title="Ringkasan", url_path="ringkasan"),
        st.Page(str(root / "views" / "about.py"), title="Tentang aplikasi", url_path="tentang"),
    ]


def render_navigation(pages: list[st.Page], active: str) -> None:
    st.markdown(
        """
        <div class="hf-header">
          <a class="hf-logo" href="/" aria-label="HuntFacts, kembali ke beranda">
            <svg class="hf-logo-icon" viewBox="0 0 32 32" aria-hidden="true">
              <circle cx="14" cy="14" r="8" fill="none" stroke="currentColor" stroke-width="3"/>
              <path d="m20 20 7 7" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
            <span>HuntFacts</span>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(len(pages))
    for column, page in zip(columns, pages):
        with column:
            if page.title == active:
                st.markdown(
                    f'<div class="hf-nav-active" aria-current="page">{page.title}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.page_link(
                    page,
                    label=page.title,
                    help=f"Buka halaman {page.title}",
                    icon=None,
                )
