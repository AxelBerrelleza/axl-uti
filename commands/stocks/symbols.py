import json
from pathlib import Path

from commands.errors import ConfigInvalidError, ConfigMissingError
from commands.stocks.errors import SymbolNotFoundError


def _find_config() -> Path | None:
    candidates = [
        Path("./symbols.json"),
        Path.home() / ".axl-uti" / "symbols.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def resolve(ticker: str) -> str:
    config_path = _find_config()
    if config_path is None:
        raise ConfigMissingError(
            "Symbol config not found. "
            "Create ~/.axl-uti/symbols.json (see symbols.example.json for format)."
        )

    try:
        data: dict = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigInvalidError(f"Invalid JSON in symbol config '{config_path}': {exc}") from exc

    if ticker not in data:
        available = ", ".join(sorted(data.keys()))
        raise SymbolNotFoundError(ticker=ticker, available=available)

    return data[ticker]
