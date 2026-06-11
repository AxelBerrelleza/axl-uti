import typer
from .morning_star import *
from .symbols import resolve as _resolve_symbol
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from typing import Optional, List
from rich import print
from .SpreedSheetComparation import SpreadSheetComparation
from commands.utils.tables import Tables

stocks_app = typer.Typer()
console = Console()
TypeOfPerformanceIdOption = Annotated[Optional[bool], typer.Option(help="Do the request with PerformanceId instead of symbol")]

@stocks_app.command(help="Find companies, ETFs inside and outside the United States")
def search(text: str):
    response = morning_star.autocomplete(text)

    console.print(Tables.from_list(response, columns=[
        "Name",
        ("Region & symbol", "RegionAndTicker"),
        ("Type", "TypeName"),
        ("Exchange", "ExchangeShortName"),
        "PerformanceId",
        "Instrument",
    ]))

def getPerformanceIdBySymbol(symbol: str, byPass: bool):
    if byPass:
        return symbol
    else:
        return _resolve_symbol(symbol)

@stocks_app.command(help="Retrieve financial info of a symbol")
def financials(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)

    print(morning_star.getFinancials(performanceId=performanceId))

@stocks_app.command(help="Show key stats of a symbol")
def overview(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
    response = morning_star.getOverview(performanceId)

    print("Valuation")
    console.print(Tables.from_dict(response['valuationRatio']))

    print("Profiability")
    console.print(Tables.from_dict(response['profitabilityRatio']))

    print("Financial Health")
    console.print(Tables.from_dict(response['financialHealth']))

    print("Efficiency")
    console.print(Tables.from_dict(response['efficiencyRatio']))

    print("Growth")
    console.print(Tables.from_dict(response['growthRatio']))
    console.print(Tables.from_dict(response['keyStatsQuoteJson']['revenue3YearGrowth']))
    console.print(Tables.from_dict(response['keyStatsQuoteJson']['netIncome3YearGrowth']))

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

    for data in response:
        color = 'green' if data['dayChange'] >= 0 else 'red'
        currency_fmt_str = data['currencySymbol'] + '{:,.3f}'
        colored_fmt_str = '[%s]%s' % (color, data['currencySymbol']) + '{:,.3f}'
        data['_last'] = colored_fmt_str.format(data['lastPrice'])
        data['_pct'] = '[%s]%.3f%%' % (color, data['dayChangePer'])
        data['_change'] = colored_fmt_str.format(data['dayChange'])
        data['_close'] = currency_fmt_str.format(data['lastClose'])
        data['_high'] = currency_fmt_str.format(data['yearRangeHigh'])
        data['_low'] = currency_fmt_str.format(data['yearRangeLow'])
        data['_mcap'] = currency_fmt_str.format(data['marketCap'])

    console.print(Tables.from_list(response, columns=[
        ("Last", "_last"),
        ("%", "_pct"),
        ("Change", "_change"),
        ("Last close", "_close"),
        ("52w High", "_high"),
        ("52w Low", "_low"),
        ("MarketCap", "_mcap"),
        ("Currency", "currencyCode"),
        ("ExchangeId", "exchangeID"),
    ]))

@stocks_app.command(name='avg-valuation')
def avgValuation(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
    response = morning_star.getAvgValuation(performanceId)
    
    headers: list = response['Collapsed']['columnDefs']
    del headers[0]
    headers.reverse()
    table = Table("Metric", *headers)
    joinedRows = response['Collapsed']['rows'] + response['Expanded']['rows']
    for row in joinedRows:
        values: list = row['datum']
        values.reverse()
        table.add_row(
            row['label'],
            *values,
            end_section=True
        )

    console.print(table)

    footer = response['Collapsed']['footer']
    print(
        f'As of "{footer['asOfDate'][:-7]}", Index is: {footer['indexName']}. Currency: {footer['enterpriseValueCurrency']}'
    )

@stocks_app.command(name='operating-efficiency')
def operatingEfficiency(symbol: str, pid: TypeOfPerformanceIdOption = False):
    performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
    response = morning_star.getOperatingEfficency(performanceId)

    data: list = response['dataList']

    date_fmt = lambda v: v[:10]
    num_fmt = lambda v: '%.3f' % v

    console.print(Tables.from_list(data, columns=[
        ("FY", "fiscalPeriodYear", date_fmt),
        ("MS-end-date", "morningstarEndingDate", date_fmt),
        ("Gross Mrgn", "grossMargin", num_fmt),
        ("Operating Mrgn", "operatingMargin", num_fmt),
        ("Net Mrgn", "netMargin", num_fmt),
        ("Ebitda Mrgn", "ebitdaMargin", num_fmt),
        ("TaxRate", "taxRate", num_fmt),
        ("ROA", "roa", num_fmt),
        ("ROE", "roe", num_fmt),
        ("ROIC", "roic", num_fmt),
        ("Interest Coverage", "interestCoverage", num_fmt),
    ]))

    console.print(Tables.from_list(data, columns=[
        ("FY", "fiscalPeriodYear", date_fmt),
        ("MS-end-date", "morningstarEndingDate", date_fmt),
        ("DaysInSales", "daysInSales", num_fmt),
        ("DaysInInventory", "daysInInventory", num_fmt),
        ("DaysInPayment", "daysInPayment", num_fmt),
        ("CashConversionCycle", "cashConversionCycle", num_fmt),
        ("ReceivableTurnover", "receivableTurnover", num_fmt),
        ("InventoryTurnover", "inventoryTurnover", num_fmt),
        ("FixedAssetsTurnover", "fixedAssetsTurnover", num_fmt),
        ("AssetsTurnover", "assetsTurnover", num_fmt),
    ]))

@stocks_app.command()
def comparator(symbols: List[str], pid: TypeOfPerformanceIdOption = False):
    performanceIds = list(getPerformanceIdBySymbol(symbol, byPass=pid) for symbol in symbols)
    
    comparation = SpreadSheetComparation()
    comparation.symbols = symbols
    comparation.performanceIds = performanceIds
    comparation.do()