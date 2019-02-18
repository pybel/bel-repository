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
    license: Optional[str] = None
    copyright: Optional[str] = None
    disclaimer: Optional[str] = None

    def new(self) -> BELGraph:
        """Generate a new BEL graph with the given metadata."""
        graph = BELGraph()
        self.update(graph)
        return graph

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
        if self.license:
            graph.licenses = self.license
        if self.copyright:
            graph.copyright = self.copyright
        if self.disclaimer:
            graph.disclaimer = self.disclaimer
