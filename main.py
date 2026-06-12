import logging

import typer
from commands.hello import app as hello
from commands.stocks import stocks_app

app = typer.Typer()


@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Show full tracebacks on errors"),
):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)


app.add_typer(hello)
app.add_typer(stocks_app, name="stocks", help="Stock related utilities, e.g. prices, indices, etc.")

if __name__ == '__main__':
    app()
