import typer
from .morning_star import *
from .symbols import symbols
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from typing import Optional
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
            row["PerformanceId"]
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