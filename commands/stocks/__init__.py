import traceback

import click
import typer
from rich.console import Console
from rich.table import Table
from rich import print
from typing_extensions import Annotated
from typing import Optional, List

from .morning_star import *
from .symbols import resolve as _resolve_symbol
from .SpreedSheetComparation import SpreadSheetComparation
from commands.utils.tables import Tables
from commands.errors import (
    AxlError,
    ConfigMissingError,
    ConfigInvalidError,
    APIError,
    APIAuthError,
    APIRateLimitError,
    APIServerError,
    NetworkError,
)
from commands.stocks.errors import SymbolNotFoundError, ComparatorError

stocks_app = typer.Typer()
console = Console()
err_console = Console(stderr=True)
TypeOfPerformanceIdOption = Annotated[Optional[bool], typer.Option(help="Do the request with PerformanceId instead of symbol")]


def _get_debug() -> bool:
    ctx = click.get_current_context(silent=True)
    if ctx and ctx.obj and isinstance(ctx.obj, dict):
        return ctx.obj.get("debug", False)
    return False


def _get_hint(err: AxlError) -> str | None:
    if isinstance(err, ComparatorError):
        return _get_hint(err.original_error)
    if isinstance(err, ConfigMissingError):
        return "Create ~/.axl-uti/symbols.json (see symbols.example.json for format)"
    if isinstance(err, ConfigInvalidError):
        return "Check the JSON syntax in your symbols config file"
    if isinstance(err, SymbolNotFoundError):
        if err.available:
            return f"Available: {err.available}"
        return None
    if isinstance(err, APIAuthError):
        return "Check your MS_API_KEY in .env"
    if isinstance(err, APIRateLimitError):
        return "Rate limit exceeded. Wait and try again"
    if isinstance(err, APIServerError):
        return "The Morningstar API is experiencing issues. Try again later"
    if isinstance(err, NetworkError):
        return "Network error. Check your internet connection"
    return None


def _get_code(err: AxlError) -> int:
    if isinstance(err, ComparatorError):
        return _get_code(err.original_error)
    if isinstance(err, SymbolNotFoundError):
        return 1
    if isinstance(err, (ConfigMissingError, ConfigInvalidError)):
        return 2
    return 3


def _format_error(err: AxlError) -> int:
    debug = _get_debug()
    message = str(err)
    hint = _get_hint(err)
    code = _get_code(err)

    err_console.print(f"[bold red]Error:[/bold red] {message}")
    if hint:
        err_console.print(f"[dim]{hint}[/dim]")

    if debug:
        traceback.print_exc()

    return code


def getPerformanceIdBySymbol(symbol: str, byPass: bool):
    if byPass:
        return symbol
    else:
        return _resolve_symbol(symbol)


@stocks_app.command(help="Find companies, ETFs inside and outside the United States")
def search(text: str):
    try:
        response = morning_star.autocomplete(text)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

    console.print(Tables.from_list(response, columns=[
        "Name",
        ("Region & symbol", "RegionAndTicker"),
        ("Type", "TypeName"),
        ("Exchange", "ExchangeShortName"),
        "PerformanceId",
        "Instrument",
    ]))


@stocks_app.command(help="Retrieve financial info of a symbol")
def financials(symbol: str, pid: TypeOfPerformanceIdOption = False):
    try:
        performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
        data = morning_star.getFinancials(performanceId=performanceId)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

    print(data)


@stocks_app.command(help="Show key stats of a symbol")
def overview(symbol: str, pid: TypeOfPerformanceIdOption = False):
    try:
        performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
        response = morning_star.getOverview(performanceId)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

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
    try:
        performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
        data = morning_star.getPriceVsFairValue(performanceId)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

    print(data)


@stocks_app.command(help="")
def price(symbols: List[str]):
    try:
        response = morning_star.getInstrumentsPrice(symbols)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

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
    try:
        performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
        response = morning_star.getAvgValuation(performanceId)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

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
    try:
        performanceId: str = getPerformanceIdBySymbol(symbol, byPass=pid)
        response = morning_star.getOperatingEfficency(performanceId)
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))

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
    try:
        performanceIds = list(getPerformanceIdBySymbol(symbol, byPass=pid) for symbol in symbols)
        comparation = SpreadSheetComparation()
        comparation.symbols = symbols
        comparation.performanceIds = performanceIds
        comparation.do()
    except AxlError as e:
        raise typer.Exit(code=_format_error(e))
