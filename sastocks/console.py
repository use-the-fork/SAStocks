from rich import print


class Console:
    def info(self, result: str):
        print("[green]Info: [/green]" + result)
        # "[bold red]Alert![/bold red] [green]Portal gun[/green] shooting! :boom:"

    def error(self, result: str):
        print("[red]Info: [/red]" + result)
        # "[bold red]Alert![/bold red] [green]Portal gun[/green] shooting! :boom:"


console = Console()
