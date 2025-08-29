from types import SimpleNamespace
from unittest.mock import patch

from sgpt.config import cfg

from .utils import app, cmd_args, mock_comp, runner


def _mock_models():
    return SimpleNamespace(data=[SimpleNamespace(id="gpt-3.5")])


def test_model_selection_on_not_found():
    class DummyNotFoundError(Exception):
        pass

    original = cfg["DEFAULT_MODEL"]
    with (
        patch.object(cfg, "_write"),
        patch("sgpt.utils.OpenAI") as OpenAI,
        patch("sgpt.utils.typer.prompt", return_value="gpt-3.5"),
        patch("sgpt.handlers.handler.completion") as completion,
        patch("sgpt.handlers.handler.NotFoundError", DummyNotFoundError),
    ):
        OpenAI.return_value.models.list.return_value = _mock_models()
        completion.side_effect = [DummyNotFoundError(), mock_comp("Prague")]

        result = runner.invoke(app, cmd_args("capital of the Czech Republic?"))
        assert result.exit_code == 0
        assert "Prague" in result.stdout
        assert completion.call_count == 2
        assert completion.call_args_list[0].kwargs["model"] == original
        assert completion.call_args_list[1].kwargs["model"] == "gpt-3.5"
        assert cfg["DEFAULT_MODEL"] == "gpt-3.5"

    cfg["DEFAULT_MODEL"] = original


def test_model_option_ask():
    original = cfg["DEFAULT_MODEL"]
    with (
        patch.object(cfg, "_write"),
        patch("sgpt.utils.OpenAI") as OpenAI,
        patch("sgpt.utils.typer.prompt", return_value="gpt-3.5"),
        patch("sgpt.handlers.handler.completion", return_value=mock_comp("Prague")) as completion,
    ):
        OpenAI.return_value.models.list.return_value = _mock_models()

        result = runner.invoke(app, cmd_args("capital?", **{"--model": "ask"}))
        assert result.exit_code == 0
        assert "Prague" in result.stdout
        completion.assert_called_once()
        assert completion.call_args.kwargs["model"] == "gpt-3.5"
        assert cfg["DEFAULT_MODEL"] == "gpt-3.5"

    cfg["DEFAULT_MODEL"] = original

