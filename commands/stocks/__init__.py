import typer
from .morning_star import *
from rich.console import Console
from rich.table import Table

stocks_app = typer.Typer()
console = Console()

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