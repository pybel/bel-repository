# -*- coding: utf-8 -*-

"""A container for BEL document metadata."""

from dataclasses import dataclass
from typing import Optional

from pybel import BELGraph

__all__ = [
    'BELMetadata',
]


@dataclass
class BELMetadata:
    """A container for BEL document metadata."""

    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    authors: Optional[str] = None
    contact: Optional[str] = None

    def update(self, graph: BELGraph) -> None:
        """Update the BEL graph's metadata."""
        if self.name:
            graph.name = self.name
        if self.version:
            graph.version = self.version
        if self.authors:
            graph.authors = self.authors
        if self.description:
            graph.description = self.description
        if self.contact:
            graph.contact = self.contact
