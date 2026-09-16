from logging import getLogger
from typing import TYPE_CHECKING
from unittest.mock import patch

from openpyxl import load_workbook
from typer.testing import CliRunner

from commands.stocks import Endpoints, stocks_app
from commands.stocks.SpreedSheetComparation import SpreadSheetComparation
from commands.tests.fixtures import APIResponses

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

runner = CliRunner()
logger = getLogger(__name__)


def test_help():
    result = runner.invoke(stocks_app, ["comparator", "--help"])
    assert result.exit_code == 0
    assert result.stdout is not None


def test_command(requests_mock):
    symbols = ["GOOGL", "AMZN"]

    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(len(symbols)))
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)

    result = runner.invoke(stocks_app, ["comparator", *symbols])

    logger.debug(result.stdout)
    assert "Loading" in result.stdout
    assert "Finished" in result.stdout

    xlDoc = load_workbook(filename="comparation.xlsx", data_only=True)
    sheet: Worksheet = xlDoc.active
    initColumn = SpreadSheetComparation.initialColumn
    initRow = SpreadSheetComparation.initialRow
    rowMap = SpreadSheetComparation.rowMap

    iter = 0
    for cells in sheet.iter_cols(
        min_col=initColumn, max_col=len(symbols) + initColumn - 1, min_row=initRow, max_row=40
    ):
        logger.info([c.value for c in cells[:14]])
        logger.info([c.value for c in cells[23:35]])

        assert cells[0].value == symbols[iter], "the headers"

        assert cells[rowMap["PER"] - initRow].value is not None
        assert cells[rowMap["PCF"] - initRow].value is not None
        assert cells[rowMap["PS"] - initRow].value is not None
        assert cells[rowMap["PBV"] - initRow].value is not None

        assert cells[rowMap["price"] - initRow].value is not None

        assert cells[rowMap["PER-5yr"] - initRow].value is not None
        assert cells[rowMap["PCF-5yr"] - initRow].value is not None
        assert cells[rowMap["PS-5yr"] - initRow].value is not None
        assert cells[rowMap["PBV-5yr"] - initRow].value is not None

        iter += 1


def test_comparator_api_error_shows_phase_and_symbol(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    requests_mock.get(Endpoints.INSTRUMENTS, status_code=500)
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)

    result = runner.invoke(stocks_app, ["comparator", "GOOGL", "AMZN"])

    assert result.exit_code == 3
    assert "Error:" in result.stdout
    assert "Failed loading price" in result.stdout
    assert "Traceback (most recent call last)" not in result.stdout


def test_comparator_overview_error_shows_symbol(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, status_code=500)
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(2))
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)

    result = runner.invoke(stocks_app, ["comparator", "GOOGL", "AMZN"])

    assert result.exit_code == 3
    assert "Error:" in result.stdout
    assert "Failed loading overview for 'GOOGL'" in result.stdout
    assert "Traceback (most recent call last)" not in result.stdout


def test_command_with_fallback_adapter(requests_mock):
    symbols = ["GOOGL", "AMZN"]
    oe_url = "https://morning-star.p.rapidapi.com/stock/v2/key-stats/get-operating-efficiency/"

    requests_mock.get(Endpoints.FINANCIAL_HEALTH, json=APIResponses.MS.FINANCIAL_HEALTH)
    requests_mock.get(oe_url, json=APIResponses.MS.OPERATING_EFFICIENCY)
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(len(symbols)))

    with patch("commands.stocks.SpreedSheetComparation.USE_FALLBACK_ADAPTER", True):
        result = runner.invoke(stocks_app, ["comparator", *symbols])

    logger.debug(result.stdout)
    assert "Loading" in result.stdout
    assert "Finished" in result.stdout

    xlDoc = load_workbook(filename="comparation.xlsx", data_only=True)
    sheet: Worksheet = xlDoc.active
    initColumn = SpreadSheetComparation.initialColumn
    initRow = SpreadSheetComparation.initialRow
    rowMap = SpreadSheetComparation.rowMap

    iter = 0
    for cells in sheet.iter_cols(
        min_col=initColumn, max_col=len(symbols) + initColumn - 1, min_row=initRow, max_row=40
    ):
        assert cells[0].value == symbols[iter]

        assert cells[rowMap["currentRatio"] - initRow].value == 2.0431
        assert cells[rowMap["quickRatio"] - initRow].value == 1.4266
        assert cells[rowMap["debtToEquity"] - initRow].value == 0.16
        assert cells[rowMap["roe"] - initRow].value == 30.5
        assert cells[rowMap["netMargin"] - initRow].value == 25.1
        assert cells[rowMap["PER"] - initRow].value is not None
        assert cells[rowMap["PCF"] - initRow].value is not None
        assert cells[rowMap["PS"] - initRow].value is not None
        assert cells[rowMap["PBV"] - initRow].value is not None

        assert cells[rowMap["price"] - initRow].value is not None
        assert cells[rowMap["PER-5yr"] - initRow].value is not None
        assert cells[rowMap["PCF-5yr"] - initRow].value is not None
        assert cells[rowMap["PS-5yr"] - initRow].value is not None
        assert cells[rowMap["PBV-5yr"] - initRow].value is not None

        iter += 1


def test_fallback_adapter_notice_printed(requests_mock):
    symbols = ["GOOGL"]
    oe_url = "https://morning-star.p.rapidapi.com/stock/v2/key-stats/get-operating-efficiency/"

    requests_mock.get(Endpoints.FINANCIAL_HEALTH, json=APIResponses.MS.FINANCIAL_HEALTH)
    requests_mock.get(oe_url, json=APIResponses.MS.OPERATING_EFFICIENCY)
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(len(symbols)))

    with patch("commands.stocks.SpreedSheetComparation.USE_FALLBACK_ADAPTER", True):
        result = runner.invoke(stocks_app, ["comparator", *symbols])

    assert result.exit_code == 0
    assert "Using adapter: FallbackAdapter" in result.stdout


def test_overview_adapter_notice_printed(requests_mock):
    symbols = ["GOOGL"]

    requests_mock.get(Endpoints.OVERVIEW, json=APIResponses.MS.OVERVIEW)
    requests_mock.get(Endpoints.INSTRUMENTS, json=APIResponses.MS.instruments(len(symbols)))
    requests_mock.get(Endpoints.AVG_VALUATION, json=APIResponses.MS.AVG_VALUATION)

    with patch("commands.stocks.SpreedSheetComparation.USE_FALLBACK_ADAPTER", False):
        result = runner.invoke(stocks_app, ["comparator", *symbols])

    assert result.exit_code == 0
    assert "Using adapter: OverviewAdapter" in result.stdout
