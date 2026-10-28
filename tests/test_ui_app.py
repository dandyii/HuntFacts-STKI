from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
VIEWS = [
    "home.py",
    "search.py",
    "evaluation.py",
    "summary.py",
    "about.py",
]


def load_page(name: str) -> AppTest:
    return AppTest.from_file(ROOT / "views" / name, default_timeout=30).run()


def test_each_view_loads_without_exception():
    for name in VIEWS:
        app = load_page(name)
        assert not app.exception, name


def test_search_examples_clear_and_submit_without_exception():
    app = load_page("search.py")
    examples = app.button
    assert len(examples) >= 5

    for index in range(3):
        app.button[index].click().run()
        assert not app.exception
        assert app.text_area[0].value

    app.text_area[0].set_value(
        "info relawan nakes pasien covid wisma atlet jakarta"
    ).run()
    app.button[3].click().run()
    assert not app.exception

    app.button[4].click().run()
    assert not app.exception
    assert app.text_area[0].value == ""
