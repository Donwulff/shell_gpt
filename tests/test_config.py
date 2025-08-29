import os

from sgpt.config import Config, DEFAULT_CONFIG


def test_system_config_overridden_by_local(tmp_path, monkeypatch):
    system_cfg = tmp_path / "system.sgptrc"
    system_cfg.write_text("DEFAULT_MODEL=gpt-3.5\nFOO=bar\n")

    local_dir = tmp_path / "user"
    local_dir.mkdir()
    local_cfg = local_dir / "sgptrc"
    local_cfg.write_text("DEFAULT_MODEL=gpt-4\n")

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    cfg = Config(local_cfg, system_config_path=system_cfg, **DEFAULT_CONFIG)

    assert cfg.get("DEFAULT_MODEL") == "gpt-4"
    assert cfg.get("FOO") == "bar"


def test_no_local_config_when_system_exists(tmp_path, monkeypatch):
    system_cfg = tmp_path / "system.sgptrc"
    system_cfg.write_text("DEFAULT_MODEL=gpt-3.5\n")

    local_cfg = tmp_path / "sgptrc"

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    Config(local_cfg, system_config_path=system_cfg, **DEFAULT_CONFIG)

    assert not local_cfg.exists()


def test_expanduser(tmp_path, monkeypatch):
    system_cfg = tmp_path / "system.sgptrc"
    system_cfg.write_text("FOO=~/bar\n")

    local_cfg = tmp_path / "sgptrc"

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    cfg = Config(local_cfg, system_config_path=system_cfg, **DEFAULT_CONFIG)

    assert cfg.get("FOO") == os.path.expanduser("~/bar")
