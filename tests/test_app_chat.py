from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_ai_page_explains_missing_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20)
    app.run()
    app.radio[0].set_value("AI Assistant").run()
    assert not app.exception
    assert any("needs a newly generated Groq API key" in warning.value for warning in app.warning)
