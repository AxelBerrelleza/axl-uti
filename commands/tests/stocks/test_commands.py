from unittest.mock import patch

import pytest
import requests
from typer.testing import CliRunner
from commands.stocks import stocks_app, Endpoints
from commands.tests.fixtures import APIResponses
from commands.errors import (
    ConfigMissingError,
    ConfigInvalidError,
)
from commands.stocks.errors import SymbolNotFoundError

runner = CliRunner()

def test_search(requests_mock):
    requests_mock.get(
        "https://morning-star.p.rapidapi.com/market/v3/auto-complete",
        json=APIResponses.MS.AUTOCOMPLETE,
    )
    result = runner.invoke(stocks_app, ['search', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0

    headers = ("Name", "Region & symbol", "Type", "Exchange", "PerformanceId", "Instrument")
    for header in headers:
        assert header in result.stdout, f"Missing header: {header}"

    assert "Apple Inc" in result.stdout
    assert "US | AAPL" in result.stdout
    assert "Equity" in result.stdout
    assert "XNAS" in result.stdout
    assert "0P000000GY" in result.stdout
    assert "126.1.AAPL" in result.stdout

    assert "Apple Hospitality REIT Inc" in result.stdout
    assert "126.1.APLE" in result.stdout

def test_financials(requests_mock):
    requests_mock.get("https://morning-star.p.rapidapi.com/stock/v2/get-financials", json={"mock": "financials"})
    result = runner.invoke(stocks_app, ['financials', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "financials" in result.stdout

def test_overview(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    result = runner.invoke(stocks_app, ['overview', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0

    sections = ("Valuation", "Profiability", "Financial Health", "Efficiency", "Growth", "VS Industry")
    for section in sections:
        assert section in result.stdout, f"Missing section: {section}"

    for header in ("priceToBook", "priceToCashFlow", "priceToSales", "priceToEPS"):
        assert header in result.stdout

def test_price_vs_fair_value(requests_mock):
    requests_mock.get("https://morning-star.p.rapidapi.com/stock/v2/get-price-fair-value/", json={"mock": "fair_value"})
    result = runner.invoke(stocks_app, ['price-vs-fair-value', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "fair_value" in result.stdout

def test_price(requests_mock):
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(1))
    result = runner.invoke(stocks_app, ['price', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "$" in result.stdout

    headers = ("Last", "%", "Change", "Last close", "52w High", "52w Low", "MarketCap", "Currency", "ExchangeId")
    for header in headers:
        assert header in result.stdout, f"Missing header: {header}"

def test_avg_valuation(requests_mock):
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)
    result = runner.invoke(stocks_app, ['avg-valuation', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0

    assert "Metric" in result.stdout
    assert "Price/Sales" in result.stdout
    assert "Price/Earnings" in result.stdout
    assert "Price/Cash Flow" in result.stdout
    assert "Price/Book" in result.stdout

def test_operating_efficiency(requests_mock):
    mock_data = {
        "dataList": [
            {
                "fiscalPeriodYear": "2024",
                "morningstarEndingDate": "2024-12-31",
                "grossMargin": 44.5,
                "operatingMargin": 30.2,
                "netMargin": 25.1,
                "ebitdaMargin": 35.0,
                "taxRate": 21.0,
                "roa": 15.2,
                "roe": 30.5,
                "roic": 20.1,
                "interestCoverage": 10.0,
                "daysInSales": 30.0,
                "daysInInventory": 40.0,
                "daysInPayment": 35.0,
                "cashConversionCycle": 35.0,
                "receivableTurnover": 12.0,
                "inventoryTurnover": 9.0,
                "fixedAssetsTurnover": 5.0,
                "assetsTurnover": 0.8
            }
        ]
    }
    requests_mock.get("https://morning-star.p.rapidapi.com/stock/v2/key-stats/get-operating-efficiency/", json=mock_data)
    result = runner.invoke(stocks_app, ['operating-efficiency', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "2024" in result.stdout
    assert "44.500" in result.stdout

    first_table_headers = (
        "FY", "MS-end-date", "Gross Mrgn", "Operating Mrgn", "Net Mrgn", "Ebitda Mrgn",
        "TaxRate", "ROA", "ROE", "ROIC", "Interest Coverage",
    )
    for header in first_table_headers:
        assert header in result.stdout, f"Missing header: {header}"

    second_table_headers = (
        "DaysInSales", "DaysInInventory", "DaysInPayment",
        "CashConversionCycle", "ReceivableTurnover", "InventoryTurnover",
        "FixedAssetsTurnover", "AssetsTurnover",
    )
    for header in second_table_headers:
        assert header in result.stdout, f"Missing header: {header}"


def _assert_no_traceback(output: str):
    assert "Traceback (most recent call last)" not in output
    assert 'File "' not in output


class TestErrorHandling:
    def test_missing_config_returns_exit_code_2(self):
        with patch(
            "commands.stocks.getPerformanceIdBySymbol",
            side_effect=ConfigMissingError("Test config missing"),
        ):
            result = runner.invoke(stocks_app, ["overview", "AAPL"])
        assert result.exit_code == 2
        assert "Error:" in result.stdout
        assert "config" in result.stdout.lower()
        _assert_no_traceback(result.stdout)

    def test_invalid_config_returns_exit_code_2(self):
        with patch(
            "commands.stocks.getPerformanceIdBySymbol",
            side_effect=ConfigInvalidError("Invalid JSON in config"),
        ):
            result = runner.invoke(stocks_app, ["overview", "AAPL"])
        assert result.exit_code == 2
        assert "Error:" in result.stdout
        assert "JSON" in result.stdout
        _assert_no_traceback(result.stdout)

    def test_unknown_ticker_returns_exit_code_1(self):
        error = SymbolNotFoundError(ticker="XYZ", available="AAPL, MSFT")
        with patch(
            "commands.stocks.getPerformanceIdBySymbol",
            side_effect=error,
        ):
            result = runner.invoke(stocks_app, ["overview", "XYZ"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "XYZ" in result.stdout
        _assert_no_traceback(result.stdout)

    def test_api_401_returns_exit_code_3(self, requests_mock):
        requests_mock.get(
            "https://morning-star.p.rapidapi.com/market/v3/auto-complete",
            status_code=401,
        )
        result = runner.invoke(stocks_app, ["search", "AAPL"])
        assert result.exit_code == 3
        assert "Error:" in result.stdout
        assert "401" in result.stdout
        _assert_no_traceback(result.stdout)

    def test_api_500_returns_exit_code_3(self, requests_mock):
        requests_mock.get(
            "https://morning-star.p.rapidapi.com/market/v3/auto-complete",
            status_code=500,
        )
        result = runner.invoke(stocks_app, ["search", "AAPL"])
        assert result.exit_code == 3
        assert "Error:" in result.stdout
        _assert_no_traceback(result.stdout)

    def test_network_timeout_returns_exit_code_3(self, requests_mock):
        requests_mock.get(
            "https://morning-star.p.rapidapi.com/market/v3/auto-complete",
            exc=requests.exceptions.Timeout,
        )
        result = runner.invoke(stocks_app, ["search", "AAPL"])
        assert result.exit_code == 3
        assert "Error:" in result.stdout
        assert "Network" in result.stdout
        _assert_no_traceback(result.stdout)

    def test_debug_flag_shows_traceback(self, requests_mock):
        from main import app

        requests_mock.get(
            "https://morning-star.p.rapidapi.com/market/v3/auto-complete",
            status_code=500,
        )
        result = runner.invoke(app, ["--debug", "stocks", "search", "AAPL"])
        assert result.exit_code == 3
        assert "Error:" in result.stdout
        assert "Traceback (most recent call last)" in result.stdout


def test_competitors(requests_mock):
    requests_mock.get(
        Endpoints.COMPETITORS,
        json=APIResponses.MS.COMPETITORS,
    )
    result = runner.invoke(stocks_app, ["competitors", "AAPL"], env={"COLUMNS": "200"})
    assert result.exit_code == 0

    headers = ("Ticker", "Name", "Price", "Currency", "P/E", "Price/Sales", "Op. Margin", "Rev. Growth")
    for header in headers:
        assert header in result.stdout, f"Missing header: {header}"

    assert "002594" in result.stdout
    assert "BYD Co Ltd Class A" in result.stdout
    assert "89.80" in result.stdout
    assert "CNY" in result.stdout
    assert "41.19" in result.stdout
    assert "4.70%" in result.stdout
    assert "-11.82%" in result.stdout
    assert "1.08" in result.stdout

    assert "RIVN" in result.stdout
    assert "Rivian Automotive Inc Class A" in result.stdout
    assert "15.54" in result.stdout
    assert "USD" in result.stdout
    assert "—" in result.stdout
    assert "-68.94%" in result.stdout
    assert "11.37%" in result.stdout
    assert "3.45" in result.stdout


def test_competitors_empty(requests_mock):
    empty_response = {
        "main": APIResponses.MS.COMPETITORS["main"],
        "competitors": [],
        "quantCompetitors": [],
    }
    requests_mock.get(
        Endpoints.COMPETITORS,
        json=empty_response,
    )
    result = runner.invoke(stocks_app, ["competitors", "AAPL"], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "No competitors found for AAPL" in result.stdout
