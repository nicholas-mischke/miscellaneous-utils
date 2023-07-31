
import typer


app = typer.Typer()


@app.command()
def hello():
    typer.echo("Utils says hello!")