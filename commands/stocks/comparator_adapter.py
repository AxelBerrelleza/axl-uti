from abc import ABC, abstractmethod

from commands.stocks.comparator_input import ComparatorInput
from commands.stocks.morning_star import (
    getOverview,
    getFinancialHealth,
    getOperatingEfficency,
    getAvgValuation,
)
from commands.stocks.errors import ComparatorError


class ComparatorDataAdapter(ABC):
    @abstractmethod
    def fetch(self, performanceId: str) -> ComparatorInput:
        pass


class OverviewAdapter(ComparatorDataAdapter):
    def fetch(self, performanceId: str) -> ComparatorInput:
        response = getOverview(performanceId)
        return ComparatorInput(
            currentRatio=response['financialHealth']['currentRatio'],
            quickRatio=response['financialHealth']['quickRatio'],
            debtToEquity=response['financialHealth']['debtToEquity'],
            roe=response['efficiencyRatio']['returnOnEquity'],
            netMargin=response['profitabilityRatio']['netMargin'],
            per=response['valuationRatio']['priceToEPS'],
            pcf=response['valuationRatio']['priceToCashFlow'],
            ps=response['valuationRatio']['priceToSales'],
            pbv=response['valuationRatio']['priceToBook'],
        )


class FallbackAdapter(ComparatorDataAdapter):
    def fetch(self, performanceId: str) -> ComparatorInput:
        fh = self._fetch_financial_health(performanceId)
        oe = self._fetch_operating_efficiency(performanceId)
        val = self._fetch_valuation(performanceId)

        return ComparatorInput(
            currentRatio=fh.get('currentRatio'),
            quickRatio=fh.get('quickRatio'),
            debtToEquity=fh.get('debtEquityRatio'),
            roe=oe.get('roe'),
            netMargin=oe.get('netMargin'),
            per=val['per'],
            pcf=val['pcf'],
            ps=val['ps'],
            pbv=val['pbv'],
        )

    def _fetch_financial_health(self, performanceId: str) -> dict:
        response = getFinancialHealth(performanceId)
        data_list = response.get('dataList', [])
        if not data_list:
            raise ComparatorError(
                phase="overview",
                original_error=Exception("No financial health data available"),
            )
        return data_list[-1]

    def _fetch_operating_efficiency(self, performanceId: str) -> dict:
        response = getOperatingEfficency(performanceId)
        data_list = response.get('dataList', [])
        result = {}
        for entry in reversed(data_list):
            if 'roe' not in result and entry.get('roe') is not None:
                result['roe'] = entry['roe']
            if 'netMargin' not in result and entry.get('netMargin') is not None:
                result['netMargin'] = entry['netMargin']
            if 'roe' in result and 'netMargin' in result:
                break
        return result

    def _fetch_valuation(self, performanceId: str) -> dict:
        response = getAvgValuation(performanceId)
        rows = response['Collapsed']['rows']

        PS_INDEX = 0
        PER_INDEX = 1
        PCF_INDEX = 2
        PBV_INDEX = 3

        def _latest_non_null(index):
            datum = rows[index]['datum']
            for val in reversed(datum):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    continue
            return None

        return {
            'ps': _latest_non_null(PS_INDEX),
            'per': _latest_non_null(PER_INDEX),
            'pcf': _latest_non_null(PCF_INDEX),
            'pbv': _latest_non_null(PBV_INDEX),
        }
