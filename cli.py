import click
from client_cli import client

@click.group()
def cli():
   
    pass

cli.add_command(client)

if __name__ == '__main__':
    cli()
