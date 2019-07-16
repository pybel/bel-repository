# -*- coding: utf-8 -*-

"""Version information for :mod:`bel-repository`."""

__all__ = [
    'VERSION',
    'get_version',
]

VERSION = '0.0.8-dev'


def get_version() -> str:
    """Get the software verison of :mod:`bel-repository`."""
    return VERSION
