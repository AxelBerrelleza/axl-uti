import typer
from .morning_star import *
from pprint import pprint

stocks_app = typer.Typer()

@stocks_app.command()
def search(text: str):
    pprint(morning_star.autocomplete(text))