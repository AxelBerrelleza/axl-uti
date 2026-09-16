from unittest.mock import patch

import pytest

from commands.errors import APIServerError
from commands.stocks.comparator_adapter import (
    FallbackAdapter,
    OverviewAdapter,
)
from commands.stocks.comparator_input import ComparatorInput
from commands.stocks.errors import ComparatorError
from commands.tests.fixtures import APIResponses


class TestComparatorInput:
    def test_all_fields_set(self):
        ci = ComparatorInput(
            currentRatio=1.5,
            quickRatio=1.2,
            debtToEquity=0.3,
            roe=0.25,
            netMargin=0.15,
            per=20.0,
            pcf=15.0,
            ps=5.0,
            pbv=3.0,
        )
        assert ci.currentRatio == 1.5
        assert ci.quickRatio == 1.2
        assert ci.debtToEquity == 0.3
        assert ci.roe == 0.25
        assert ci.netMargin == 0.15
        assert ci.per == 20.0
        assert ci.pcf == 15.0
        assert ci.ps == 5.0
        assert ci.pbv == 3.0

    def test_defaults_are_none(self):
        ci = ComparatorInput()
        assert ci.currentRatio is None
        assert ci.quickRatio is None
        assert ci.debtToEquity is None
        assert ci.roe is None
        assert ci.netMargin is None
        assert ci.per is None
        assert ci.pcf is None
        assert ci.ps is None
        assert ci.pbv is None

    def test_partial_fields(self):
        ci = ComparatorInput(currentRatio=1.5, roe=0.25)
        assert ci.currentRatio == 1.5
        assert ci.roe == 0.25
        assert ci.quickRatio is None
        assert ci.per is None


class TestOverviewAdapter:
    def test_fetch_returns_populated_input(self):
        adapter = OverviewAdapter()
        with patch(
            "commands.stocks.comparator_adapter.getOverview", return_value=APIResponses.MS.OVERVIEW
        ):
            result = adapter.fetch("0P000002HD")

        assert isinstance(result, ComparatorInput)
        assert result.currentRatio == 1.35082
        assert result.quickRatio == 1.099713
        assert result.debtToEquity == 0.205567
        assert result.roe == 0.342907
        assert result.netMargin == 0.354275
        assert result.per == 31.630137
        assert result.pcf == 23.364486
        assert result.ps == 11.198208
        assert result.pbv == 9.643202

    def test_fetch_raises_on_api_error(self):
        adapter = OverviewAdapter()
        with (
            patch(
                "commands.stocks.comparator_adapter.getOverview",
                side_effect=APIServerError(503, "/overview"),
            ),
            pytest.raises(APIServerError),
        ):
            adapter.fetch("0P000002HD")


class TestFallbackAdapter:
    def test_fetch_returns_populated_input(self):
        adapter = FallbackAdapter()
        with (
            patch(
                "commands.stocks.comparator_adapter.getFinancialHealth",
                return_value=APIResponses.MS.FINANCIAL_HEALTH,
            ),
            patch(
                "commands.stocks.comparator_adapter.getOperatingEfficency",
                return_value=APIResponses.MS.OPERATING_EFFICIENCY,
            ),
            patch(
                "commands.stocks.comparator_adapter.getAvgValuation",
                return_value=APIResponses.MS.AVG_VALUATION,
            ),
        ):
            result = adapter.fetch("0P000002HD")

        assert isinstance(result, ComparatorInput)
        assert result.currentRatio == 2.0431
        assert result.quickRatio == 1.4266
        assert result.debtToEquity == 0.16
        assert result.roe == 30.5
        assert result.netMargin == 25.1
        assert result.per is not None
        assert result.pcf is not None
        assert result.ps is not None
        assert result.pbv is not None

    def test_fetch_empty_financial_health_raises(self):
        adapter = FallbackAdapter()
        empty_response = {"currency": "USD", "asOfDate": "2026-03-31", "dataList": []}
        with (
            patch(
                "commands.stocks.comparator_adapter.getFinancialHealth", return_value=empty_response
            ),
            pytest.raises(ComparatorError, match="No financial health data"),
        ):
            adapter.fetch("0P000002HD")

    def test_fetch_missing_fields_returns_none(self):
        adapter = FallbackAdapter()
        partial_fh = {"dataList": [{"fiscalPeriodYearMonth": "Latest Qtr", "currentRatio": 2.0}]}
        empty_oe = {"dataList": []}
        with (
            patch("commands.stocks.comparator_adapter.getFinancialHealth", return_value=partial_fh),
            patch(
                "commands.stocks.comparator_adapter.getOperatingEfficency", return_value=empty_oe
            ),
            patch(
                "commands.stocks.comparator_adapter.getAvgValuation",
                return_value=APIResponses.MS.AVG_VALUATION,
            ),
        ):
            result = adapter.fetch("0P000002HD")

        assert result.currentRatio == 2.0
        assert result.quickRatio is None
        assert result.debtToEquity is None
        assert result.roe is None
        assert result.netMargin is None

    def test_fetch_financial_health_api_error(self):
        adapter = FallbackAdapter()
        with (
            patch(
                "commands.stocks.comparator_adapter.getFinancialHealth",
                side_effect=APIServerError(503, "/fh"),
            ),
            pytest.raises(APIServerError),
        ):
            adapter.fetch("0P000002HD")

    def test_fetch_operating_efficiency_api_error(self):
        adapter = FallbackAdapter()
        with (
            patch(
                "commands.stocks.comparator_adapter.getFinancialHealth",
                return_value=APIResponses.MS.FINANCIAL_HEALTH,
            ),
            patch(
                "commands.stocks.comparator_adapter.getOperatingEfficency",
                side_effect=APIServerError(503, "/oe"),
            ),
            pytest.raises(APIServerError),
        ):
            adapter.fetch("0P000002HD")

    def test_fetch_valuation_api_error(self):
        adapter = FallbackAdapter()
        with (
            patch(
                "commands.stocks.comparator_adapter.getFinancialHealth",
                return_value=APIResponses.MS.FINANCIAL_HEALTH,
            ),
            patch(
                "commands.stocks.comparator_adapter.getOperatingEfficency",
                return_value=APIResponses.MS.OPERATING_EFFICIENCY,
            ),
            patch(
                "commands.stocks.comparator_adapter.getAvgValuation",
                side_effect=APIServerError(503, "/val"),
            ),
            pytest.raises(APIServerError),
        ):
            adapter.fetch("0P000002HD")
