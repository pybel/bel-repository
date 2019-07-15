# -*- coding: utf-8 -*-

"""Utilities for ``bel-repository``."""

import json
from typing import Any, Iterable, Mapping, Optional, TextIO

from pybel import BELGraph

__all__ = [
    'serialize_authors',
    'to_summary_json_path',
    'to_summary_json',
]


def serialize_authors(authors: Iterable[str]) -> str:
    """Sort an author list by last name and join with commas."""
    return ', '.join(sorted(authors, key=lambda s: s.split()[-1]))


def to_summary_json_path(graph: BELGraph, path: str, **kwargs) -> None:
    """Write a summary JSON of the graph to a file at the given path."""
    with open(path, 'w') as file:
        to_summary_json_file(graph=graph, file=file, **kwargs)


def to_summary_json_file(
        graph: BELGraph,
        file: Optional[TextIO] = None,
        indent: int = 2,
        **kwargs
) -> None:
    """Write a summary JSON of the graph to a file."""
    json.dump(to_summary_json(graph), file, indent=indent, **kwargs)


def to_summary_json(graph: BELGraph) -> Mapping[str, Any]:
    """Get a summary JSON of the graph."""
    return {
        'Title': graph.name,
        'Authors': graph.authors,
        'Number of URL Namespaces': len(graph.namespace_url),
        'Number of Regex Namespaces': len(graph.namespace_pattern),
        'Number of URL Annotations': len(graph.annotation_url),
        'Number of Regex Annotations': len(graph.annotation_pattern),
        'Number of Local Annotations': len(graph.annotation_list),
        **graph.summary_dict()
    }
