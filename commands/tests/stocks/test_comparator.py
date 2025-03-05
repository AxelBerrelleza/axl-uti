import pytest
from typer.testing import CliRunner
from commands.stocks import stocks_app, Endpoints, getOverview

runner = CliRunner()

def test_help():
    result = runner.invoke(stocks_app, ['comparator', '--help'])
    assert result.exit_code == 0
    assert result.stdout != None

# def test_creation_of_xl_file():
def test_mock(requests_mock):
    requests_mock.get(Endpoints.OVERVIEW, json={
            'valuationRatio': {'asOfDate': '2025-02-27', 'priceToBook': 9.643202, 'priceToCashFlow': 23.364486, 'priceToSales': 11.198208, 'priceToEPS': 31.630137},
            'growthRatio': {'reportDate': '2024-06-30', 'revenue': 0.134006, 'operatingIncome': 0.161067, 'netIncome': 0.128841, 'eps': 0.135957},
            'financialHealth': {'reportDate': '2024-12-31', 'quickRatio': 1.099713, 'currentRatio': 1.35082, 'debtToEquity': 0.205567},
            'efficiencyRatio': {'reportDate': '2024-12-31', 'returnOnAssets': 0.184677, 'returnOnEquity': 0.342907, 'returnOnInvestedCapital': 0.268562},
            'profitabilityRatio': {'reportDate': '2024-12-31', 'interestCoverage': 43.439671, 'netMargin': 0.354275},
            'keyStatsQuoteJson': {
                'revenue3YearGrowth': {'stockValue': '13.4000', 'indAvg': '13.2300'},
                'netIncome3YearGrowth': {'stockValue': '12.8800', 'indAvg': '14.4900'},
                'operatingMarginTTM': {'stockValue': '44.9600', 'indAvg': '30.0000'},
                'netMarginTTM': {'stockValue': '35.4300', 'indAvg': '23.0700'},
                'roaTTM': {'stockValue': '18.4700', 'indAvg': '11.3600'},
                'roeTTM': {'stockValue': '34.2900', 'indAvg': '28.7600'},
                'debitToEquity': {'stockValue': '0.1882', 'indAvg': '0.5167'},
                'freeCashFlow': {'cashFlowTTM': '70031000000', 'date': '2024-12-31T06:00:00.000'}
            }
        })
    result = runner.invoke(stocks_app, ['comparator', 'GOOGL', 'AMZN'])
    
    print(result)
    assert 'Loading' in result.stdout
    assert 'Finished' in result.stdout