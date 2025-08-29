import os
from getpass import getpass
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Iterable

from click import UsageError

CONFIG_FOLDER = os.path.expanduser("~/.config")
SHELL_GPT_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "shell_gpt"


def _config_path(folder: Path) -> Path:
    for name in ("sgptrc", ".sgptrc"):
        path = folder / name
        if path.exists():
            return path
    return folder / "sgptrc"


SHELL_GPT_CONFIG_PATH = _config_path(SHELL_GPT_CONFIG_FOLDER)
SHELL_GPT_SYSTEM_CONFIG_PATH = _config_path(Path("/etc/shell_gpt"))

ROLE_STORAGE_PATH = SHELL_GPT_CONFIG_FOLDER / "roles"
SYSTEM_ROLE_STORAGE_PATH = Path("/etc/shell_gpt/roles")
FUNCTIONS_PATH = SHELL_GPT_CONFIG_FOLDER / "functions"
SYSTEM_FUNCTIONS_PATH = Path("/etc/shell_gpt/functions")
CHAT_CACHE_PATH = Path(gettempdir()) / "chat_cache"
CACHE_PATH = Path(gettempdir()) / "cache"

# TODO: Refactor ENV variables with SGPT_ prefix.
DEFAULT_CONFIG = {
    # TODO: Refactor it to CHAT_STORAGE_PATH.
    "CHAT_CACHE_PATH": os.getenv("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CHAT_CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "60")),
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gpt-4o"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "magenta"),
    "ROLE_STORAGE_PATH": os.getenv(
        "ROLE_STORAGE_PATH",
        os.pathsep.join([str(ROLE_STORAGE_PATH), str(SYSTEM_ROLE_STORAGE_PATH)]),
    ),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    "DISABLE_STREAMING": os.getenv("DISABLE_STREAMING", "false"),
    "CODE_THEME": os.getenv("CODE_THEME", "dracula"),
    "OPENAI_FUNCTIONS_PATH": os.getenv(
        "OPENAI_FUNCTIONS_PATH",
        os.pathsep.join([str(FUNCTIONS_PATH), str(SYSTEM_FUNCTIONS_PATH)]),
    ),
    "OPENAI_USE_FUNCTIONS": os.getenv("OPENAI_USE_FUNCTIONS", "true"),
    "SHOW_FUNCTIONS_OUTPUT": os.getenv("SHOW_FUNCTIONS_OUTPUT", "false"),
    "API_BASE_URL": os.getenv("API_BASE_URL", "default"),
    "PRETTIFY_MARKDOWN": os.getenv("PRETTIFY_MARKDOWN", "true"),
    "USE_LITELLM": os.getenv("USE_LITELLM", "false"),
    "SHELL_INTERACTION": os.getenv("SHELL_INTERACTION", "false"),
    "OS_NAME": os.getenv("OS_NAME", "auto"),
    "SHELL_NAME": os.getenv("SHELL_NAME", "auto"),
    # New features might add their own config variables here.
}


class Config(dict):  # type: ignore
    def __init__(
        self,
        config_path: Path,
        system_config_path: Path | None = None,
        **defaults: Any,
    ) -> None:
        self.config_path = config_path

        merged_defaults = dict(defaults)
        if system_config_path and system_config_path.exists():
            merged_defaults.update(self._read_file(system_config_path))

        if self._exists:
            self._read()
            missing_keys: list[str] = []
            for key, value in merged_defaults.items():
                if key not in self:
                    self[key] = value
                    missing_keys.append(key)
            if missing_keys:
                self._write(missing_keys)
        elif system_config_path and system_config_path.exists():
            super().__init__(**merged_defaults)
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            # Don't write API key to config file if it is in the environment.
            if not merged_defaults.get("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
                __api_key = getpass(prompt="Please enter your OpenAI API key: ")
                merged_defaults["OPENAI_API_KEY"] = __api_key
            super().__init__(**merged_defaults)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self, keys: Iterable[str] | None = None) -> None:
        if self._exists:
            data = self._read_file(self.config_path)
        else:
            data = {}
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

        keys_to_write = list(self.keys()) if keys is None else list(keys)
        for key in keys_to_write:
            data[key] = self[key]

        with open(self.config_path, "w", encoding="utf-8") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

    @staticmethod
    def _read_file(path: Path) -> dict[str, str]:
        result: dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    result[key] = os.path.expanduser(value)
        return result

    def _read(self) -> None:
        self.update(self._read_file(self.config_path))

    def get(self, key: str) -> str:  # type: ignore
        # Prioritize environment variables over config file.
        value = os.getenv(key) or super().get(key)
        if not value:
            raise UsageError(f"Missing config key: {key}")
        return value


cfg = Config(
    SHELL_GPT_CONFIG_PATH,
    system_config_path=SHELL_GPT_SYSTEM_CONFIG_PATH,
    **DEFAULT_CONFIG,
)
