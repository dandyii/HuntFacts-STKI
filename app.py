from pathlib import Path

import streamlit as st

from ui.navigation import build_pages
from ui.theme import load_theme


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="HuntFacts",
    page_icon=str(ROOT / "assets" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_theme()

pages = build_pages(ROOT)
navigation = st.navigation(pages, position="hidden")
navigation.run()
