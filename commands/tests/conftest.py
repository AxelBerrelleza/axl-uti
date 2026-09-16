from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_resolve_symbol():
    """Globally mock the ticker-to-PerformanceId resolution for command tests.

    This ensures that any test executing CLI commands (which resolve symbols)
    will automatically bypass the real config file lookup and use this mock.

    Note: Since test_symbols.py imports `commands.stocks.symbols` and tests its
    `resolve` function directly, this patch on `commands.stocks._resolve_symbol`
    does not interfere with test_symbols.py's unit tests.
    """
    fake_pids = {
        "GOOGL": "0P000002HD",
        "AMZN": "0P000000B7",
        "MSFT": "0P000003MH",
        "AAPL": "0P000000GY",
    }

    def side_effect(ticker):
        if ticker in fake_pids:
            return fake_pids[ticker]
        return f"MOCK_PID_{ticker}"

    with patch("commands.stocks._resolve_symbol", side_effect=side_effect) as mock:
        yield mock
