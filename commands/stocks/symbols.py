"""
Symbol config loader for axl-uti.

Loads ticker → PerformanceId mappings from a user-managed JSON config file.
Search order:
  1. ./symbols.json        (project root — dev override)
  2. ~/.axl-uti/symbols.json (user home — primary location)
"""

import json
from pathlib import Path


def _find_config() -> Path | None:
    """Return the first symbols.json path that exists, or None."""
    candidates = [
        Path("./symbols.json"),
        Path.home() / ".axl-uti" / "symbols.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def resolve(ticker: str) -> str:
    """Return the PerformanceId for *ticker*.

    Raises:
        SystemExit: if no config file is found or the JSON is invalid.
        KeyError: if the ticker is not present in the config.
    """
    config_path = _find_config()
    if config_path is None:
        raise FileNotFoundError(
            "Symbol config not found. "
            "Create ~/.axl-uti/symbols.json (see symbols.example.json for format)."
        )

    try:
        data: dict = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in symbol config '{config_path}': {exc}"
        ) from exc

    if ticker not in data:
        available = ", ".join(sorted(data.keys()))
        raise KeyError(
            f"Ticker '{ticker}' not found. Available tickers: [{available}]"
        )

    return data[ticker]