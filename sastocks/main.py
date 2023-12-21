from datetime import date, timedelta

import typer

from sastocks.pull_financials import pull_financials
from sastocks.pull_news import pull_news
from sastocks.tickers import add_ticker

app = typer.Typer()


@app.callback()
def callback():
    """
    Stock Beast
    """


@app.command()
def ticker(
    action: str = typer.Argument(..., help="The action to perform: add or remove")
):
    """
    Manage ticker symbols in the database.
    """
    if action == "add":
        symbol = typer.prompt("Enter the ticker symbol to add")
        add_ticker(symbol)
    elif action == "remove":
        typer.echo("Remove functionality not implemented yet.")
    else:
        typer.echo("Invalid action. Please use 'add' or 'remove'.")


@app.command()
def finance(
    start_date: str = typer.Option(
        (date.today() - timedelta(days=1)).isoformat(),
        "--start-date",
        help="The start date for news in YYYY-MM-DD format",
    ),
    end_date: str = typer.Option(
        date.today().isoformat(),
        "--end-date",
        help="The end date for news in YYYY-MM-DD format",
    ),
):
    """
    Load Daily Stock prices
    """
    pull_financials((start_date, end_date))


@app.command()
def news(
    start_date: str = typer.Option(
        (date.today() - timedelta(days=1)).isoformat(),
        "--start-date",
        help="The start date for news in YYYY-MM-DD format",
    ),
    end_date: str = typer.Option(
        date.today().isoformat(),
        "--end-date",
        help="The end date for news in YYYY-MM-DD format",
    ),
):
    """
    Load News
    """
    pull_news((start_date, end_date))
    typer.echo("Loading news...")
