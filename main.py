import typer
from commands.hello import app as hello

app = typer.Typer()

app.add_typer(hello)

if __name__ == '__main__':
    app()