import pytest
from typer.testing import CliRunner
from commands.stocks import stocks_app, Endpoints
from commands.tests.fixtures import APIResponses

runner = CliRunner()

def test_financials(requests_mock):
    requests_mock.get("https://morning-star.p.rapidapi.com/stock/v2/get-financials", json={"mock": "financials"})
    result = runner.invoke(stocks_app, ['financials', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "financials" in result.stdout

def test_overview(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    result = runner.invoke(stocks_app, ['overview', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "Valuation" in result.stdout

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

def test_avg_valuation(requests_mock):
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)
    result = runner.invoke(stocks_app, ['avg-valuation', 'AAPL'], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    assert "Price/Sales" in result.stdout

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
