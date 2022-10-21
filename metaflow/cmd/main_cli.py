import builtins
import traceback
from metaflow._vendor import click
import json
import os
import sys
import shutil

from os.path import expanduser

from metaflow.datastore.local_storage import LocalStorage
from metaflow.metaflow_config import DATASTORE_LOCAL_DIR
from metaflow.util import to_unicode


@click.group()
@click.pass_context
def main(ctx):
    pass


@main.command(help="Show all available commands.")
@click.pass_context
def help(ctx):
    print(ctx.parent.get_help())


@main.command(help="Show flows accessible from the current working tree.")
def status():
    from metaflow.client import get_metadata

    res = get_metadata()
    if res:
        res = res.split("@")
    else:
        raise click.ClickException("Unknown status: cannot find a Metadata provider")
    if res[0] == "service":
        echo("Using Metadata provider at: ", nl=False)
        echo('"%s"\n' % res[1], fg="cyan")
        echo("To list available flows, type:\n")
        echo("1. python")
        echo("2. from metaflow import Metaflow")
        echo("3. list(Metaflow())")
        return

    from metaflow.client import namespace, metadata, Metaflow

    # Get the local data store path
    path = LocalStorage.get_datastore_root_from_config(echo, create_on_absent=False)
    # Throw an exception
    if path is None:
        raise click.ClickException(
            "Could not find "
            + click.style('"%s"' % DATASTORE_LOCAL_DIR, fg="red")
            + " in the current working tree."
        )

    stripped_path = os.path.dirname(path)
    namespace(None)
    metadata("local@%s" % stripped_path)
    echo("Working tree found at: ", nl=False)
    echo('"%s"\n' % stripped_path, fg="cyan")
    echo("Available flows:", fg="cyan", bold=True)
    for flow in Metaflow():
        echo("* %s" % flow, fg="cyan")


@click.command(
    cls=click.CommandCollection,
    sources=_clis + [main],
    invoke_without_command=True,
)
@click.pass_context
def start(ctx):
    global echo
    echo = echo_always

    import metaflow

    echo("Metaflow ", fg="magenta", bold=True, nl=False)

    if ctx.invoked_subcommand is None:
        echo("(%s): " % metaflow.__version__, fg="magenta", bold=False, nl=False)
    else:
        echo("(%s)\n" % metaflow.__version__, fg="magenta", bold=False)

    if ctx.invoked_subcommand is None:
        echo("More data science, less engineering\n", fg="magenta")

        # metaflow URL
        echo("http://docs.metaflow.org", fg="cyan", nl=False)
        echo(" - Read the documentation")

        # metaflow chat
        echo("http://chat.metaflow.org", fg="cyan", nl=False)
        echo(" - Chat with us")

        # metaflow help email
        echo("help@metaflow.org", fg="cyan", nl=False)
        echo("        - Get help by email\n")

        print(ctx.get_help())


start()

for _n in [
    "get_modules",
    "load_module",
    "_modules_to_import",
    "m",
    "_get_clis",
    "_clis",
    "ext_debug",
    "e",
]:
    try:
        del globals()[_n]
    except KeyError:
        pass
del globals()["_n"]
