# -*- coding: utf-8 -*-

"""A command line interface for BEL repositories."""

import os

import click

from .repository import BELRepository, append_click_group

__all__ = [
    'main',
]


@click.group()
@click.version_option()
@click.option('-d', '--directory', default=os.getcwd(), type=click.Path(file_okay=False, dir_okay=True, exists=True),
              help='Defaults to current working directory')
@click.pass_context
def main(ctx, directory: str):
    """Command line interface for bel-repository."""
    ctx.obj = BELRepository(directory=directory)


append_click_group(main)

if __name__ == '__main__':
    main()
