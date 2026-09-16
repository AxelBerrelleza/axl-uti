"""Tests for commands/stocks/symbols.py loader module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import commands.stocks.symbols as sym_module
from commands.errors import ConfigInvalidError, ConfigMissingError
from commands.stocks.errors import SymbolNotFoundError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


SAMPLE_CONFIG = {"MSFT": "0P000003MH", "AAPL": "0P000000GY", "AMZN": "0P000000B7"}


# ---------------------------------------------------------------------------
# 3.2  Config found at project root → resolves correctly
# ---------------------------------------------------------------------------


def test_resolve_from_project_root(tmp_path):
    config = tmp_path / "symbols.json"
    _write_json(config, SAMPLE_CONFIG)

    with patch.object(sym_module, "_find_config", return_value=config):
        result = sym_module.resolve("MSFT")

    assert result == "0P000003MH"


# ---------------------------------------------------------------------------
# 3.3  Config found at user home (project root absent) → resolves correctly
# ---------------------------------------------------------------------------


def test_resolve_from_user_home(tmp_path):
    home_config = tmp_path / ".axl-uti" / "symbols.json"
    _write_json(home_config, SAMPLE_CONFIG)

    # Simulate _find_config returning the home path (project-root file absent)
    with patch.object(sym_module, "_find_config", return_value=home_config):
        result = sym_module.resolve("AMZN")

    assert result == "0P000000B7"


# ---------------------------------------------------------------------------
# 3.1 / priority: project root takes precedence over user home
# ---------------------------------------------------------------------------


def test_find_config_prefers_project_root(tmp_path, monkeypatch):
    """_find_config should return ./symbols.json when both locations exist."""
    # Change cwd so ./symbols.json resolves inside tmp_path
    monkeypatch.chdir(tmp_path)

    root_config = tmp_path / "symbols.json"
    _write_json(root_config, {"ROOT": "root-pid"})

    home_config = tmp_path / ".axl-uti" / "symbols.json"
    _write_json(home_config, {"HOME": "home-pid"})

    # Patch Path.home() so the "home" path resolves inside tmp_path
    with patch.object(Path, "home", return_value=tmp_path):
        found = sym_module._find_config()

    assert found is not None
    assert found.resolve() == root_config.resolve()


def test_find_config_falls_back_to_home(tmp_path, monkeypatch):
    """When ./symbols.json is absent, _find_config should return the home path."""
    monkeypatch.chdir(tmp_path)  # no symbols.json in tmp_path

    home_config = tmp_path / ".axl-uti" / "symbols.json"
    _write_json(home_config, SAMPLE_CONFIG)

    with patch.object(Path, "home", return_value=tmp_path):
        found = sym_module._find_config()

    assert found is not None
    assert found.resolve() == home_config.resolve()


# ---------------------------------------------------------------------------
# 3.4  No config file found → raises error with helpful message
# ---------------------------------------------------------------------------


def test_resolve_no_config_raises(tmp_path):
    with patch.object(sym_module, "_find_config", return_value=None):
        with pytest.raises(ConfigMissingError) as exc_info:
            sym_module.resolve("MSFT")

    assert "symbols.json" in str(exc_info.value)
    assert "symbols.example.json" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3.5  Unknown ticker → raises KeyError with available tickers listed
# ---------------------------------------------------------------------------


def test_resolve_unknown_ticker_raises_key_error(tmp_path):
    config = tmp_path / "symbols.json"
    _write_json(config, SAMPLE_CONFIG)

    with patch.object(sym_module, "_find_config", return_value=config):
        with pytest.raises(SymbolNotFoundError) as exc_info:
            sym_module.resolve("XYZ")

    error_msg = str(exc_info.value)
    assert "XYZ" in error_msg
    # At least one known ticker should appear in the list
    assert "MSFT" in error_msg or "AAPL" in error_msg or "AMZN" in error_msg


# ---------------------------------------------------------------------------
# 3.6  Invalid JSON in config → raises parse error with file path
# ---------------------------------------------------------------------------


def test_resolve_invalid_json_raises(tmp_path):
    config = tmp_path / "symbols.json"
    config.write_text("{ this is not valid json }", encoding="utf-8")

    with patch.object(sym_module, "_find_config", return_value=config):
        with pytest.raises(ConfigInvalidError) as exc_info:
            sym_module.resolve("MSFT")

    error_msg = str(exc_info.value)
    assert str(config) in error_msg
