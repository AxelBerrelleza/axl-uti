import typer
from commands.hello import app as hello
from commands.stocks import stocks_app

app = typer.Typer()

app.add_typer(hello)
app.add_typer(stocks_app, name="stocks", help="Stock related utilities, e.g. prices, indices, etc.")

if __name__ == '__main__':
    app()