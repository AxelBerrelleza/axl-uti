import typer
from .morning_star import *
from .symbols import symbols
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from typing import Optional, List
from rich import print

stocks_app = typer.Typer()
console = Console()
TypeOfPerformanceIdOption = Annotated[Optional[bool], typer.Option(help="Do the request with PerformanceId instead of symbol")]

@stocks_app.command(help="Find companies, ETFs inside and outside the United States")
def search(text: str):
    response = morning_star.autocomplete(text)

    table = Table("Name", "Region & symbol", "Type", "Exchange", "Performance Id")
    for row in response:
        table.add_row(
            row["Name"],
            row["RegionAndTicker"],
            row["TypeName"],
            row["ExchangeShortName"],
            row["PerformanceId"],
            row["Instrument"],
        )

    console.print(table)

def getPerformanceIdBySymbol(symbol: str, byPass: bool):    
    if byPass:
        return symbol
    else:
        return symbols[symbol]

@stocks_app.command(help="Retrieve financial info of a symbol")
def financials(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)

    print(morning_star.getFinancials(performanceId=performanceId))

@stocks_app.command(help="Show key stats of a symbol")
def overview(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
    response = morning_star.getOverview(performanceId)

    print("Valuation")
    table = Table(*response['valuationRatio'].keys())
    values = ( str(val) for val in response['valuationRatio'].values() )
    table.add_row(*values)
    console.print(table)

    print("Profiability")
    table = Table(*response['profitabilityRatio'].keys())
    values = ( str(val) for val in response['profitabilityRatio'].values() )
    table.add_row(*values)
    console.print(table)

    print("Financial Health")
    table = Table(*response['financialHealth'].keys())
    values = ( str(val) for val in response['financialHealth'].values() )
    table.add_row(*values)
    console.print(table)

    print("Efficiency")
    table = Table(*response['efficiencyRatio'].keys())
    values = ( str(val) for val in response['efficiencyRatio'].values() )
    table.add_row(*values)
    console.print(table)

    print("Growth")
    table = Table(*response['growthRatio'].keys())
    values = ( str(val) for val in response['growthRatio'].values() )
    table.add_row(*values)
    console.print(table)
    table = Table("Revenue 3Y Growth", "Industry Avg.")
    values = ( str(val) for val in response['keyStatsQuoteJson']['revenue3YearGrowth'].values() )
    table.add_row(*values)
    console.print(table)
    table = Table("Net Income 3Y Growth", "Industry Avg.")
    values = ( str(val) for val in response['keyStatsQuoteJson']['netIncome3YearGrowth'].values() )
    table.add_row(*values)
    console.print(table)

    print("VS Industry")
    keyStats = response['keyStatsQuoteJson']
    del keyStats['revenue3YearGrowth']
    del keyStats['netIncome3YearGrowth']
    del keyStats['freeCashFlow']
    table = Table("", *keyStats.keys())
    fromSymbol = ( str(val['stockValue']) for val in keyStats.values() )
    table.add_row("Current", *fromSymbol)
    industryAvg = ( str(val['indAvg']) for val in keyStats.values() )
    table.add_row("Industry Avg.", *industryAvg)
    console.print(table)

@stocks_app.command(name='price-vs-fair-value', help="Morningstar estimate based on how much cash they think the company will generate")
def priceVsFairValue(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
    print(morning_star.getPriceVsFairValue(performanceId))

@stocks_app.command(help="")
def price(symbols: List[str]):    
    response = morning_star.getInstrumentsPrice(symbols)

    table = Table("Last", "%", "Change", "Last close", "52w High", "52w Low", "MarketCap", "Currency", "ExchangeId")
    for data in response:
        color = 'green' if data['dayChange'] >= 0 else 'red'
        currencyF = data['currencySymbol'] + '{:,.3f}'
        withColorF = '[%s]%s' % (color, data['currencySymbol']) + '{:,.3f}'
        table.add_row(
            withColorF.format(data['lastPrice']),
            '[%s]%.3f%%' % (color, data['dayChangePer']),
            withColorF.format(data['dayChange']),
            currencyF.format(data['lastClose']),
            currencyF.format(data['yearRangeHigh']),
            currencyF.format(data['yearRangeLow']),
            currencyF.format(data['marketCap']),
            data['currencyCode'],
            data['exchangeID'],
        )

    console.print(table)