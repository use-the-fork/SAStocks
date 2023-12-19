import click

from sastocks.config import config
from sastocks.tickers import add_ticker


# Create the main command group for sastocks API CLI
@click.group(context_settings={"auto_envvar_prefix": "sastocks"})
@click.version_option(prog_name="sastocks")
def cli():
    return


@cli.command("pull")
@click.option(
    "-d",
    "--debug",
    default=False,
    is_flag=True,
    envvar="DEBUG",
    help="Set the log level to debug",
)
@click.option("--host", help="Specify a different host to run the server on")
@click.option("--port", help="Specify a different port to run the server on")
def sastocks_run_pull(debug, host, port):
    config.run.debug = debug


# Ticker command group
@cli.group()
def ticker():
    """Commands related to stock tickers."""
    pass


# Subcommand for adding a ticker
@ticker.command("add")
@click.argument("symbol")
def add_ticker_command(symbol):
    """Add a new ticker."""
    # Call the function to add a ticker - implement this function in your module
    add_ticker(symbol)
