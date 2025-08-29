from sgpt.config import Config, DEFAULT_CONFIG
from sgpt.utils import ask_for_model


def test_ask_for_model_updates_config(tmp_path, monkeypatch):
    config_path = tmp_path / "sgptrc"
    test_cfg = Config(
        config_path,
        system_config_path=None,
        **{**DEFAULT_CONFIG, "OPENAI_API_KEY": "test"},
    )
    monkeypatch.setattr("sgpt.utils.cfg", test_cfg)

    class DummyClient:
        class Models:
            def list(self):  # noqa: D401 - docstring not required
                return type(
                    "R",
                    (),
                    {
                        "data": [
                            type("M", (), {"id": "m1"}),
                            type("M", (), {"id": "m2"}),
                        ]
                    },
                )()

        models = Models()

    monkeypatch.setattr("sgpt.utils.OpenAI", lambda **_: DummyClient())
    monkeypatch.setattr("sgpt.utils.typer.prompt", lambda *a, **k: 2)
    monkeypatch.setattr("sgpt.utils.typer.echo", lambda *a, **k: None)

    selected = ask_for_model()

    assert selected == "m2"
    assert test_cfg.get("DEFAULT_MODEL") == "m2"
    assert "DEFAULT_MODEL=m2" in config_path.read_text()
