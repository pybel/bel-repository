# -*- coding: utf-8 -*-

"""Utilities for ``bel-repository``."""

import json
from typing import Any, List, Mapping

from pybel import BELGraph

__all__ = [
    'serialize_authors',
    'to_summary_json_path',
    'to_summary_json',
]


def serialize_authors(authors: List[str]) -> str:
    """Sort an author list by last name and join with commas."""
    return ', '.join(sorted(authors, key=lambda s: s.split()[-1]))


def to_summary_json_path(graph: BELGraph, path: str) -> None:
    """Write a summary JSON of the graph."""
    with open(path, 'w') as file:
        json.dump(to_summary_json(graph), file)


def to_summary_json(graph: BELGraph) -> Mapping[str, Any]:
    """Get a summary JSON of the graph."""
    rv = dict(
        Title=graph.name,
        Authors=graph.authors,
        **graph.summary_dict()
    )
    rv['Number of URL Namespaces'] = len(graph.namespace_url)
    rv['Number of Regex Namespaces'] = len(graph.namespace_pattern)
    rv['Number of URL Annotations'] = len(graph.annotation_url)
    rv['Number of Regex Annotations'] = len(graph.annotation_pattern)
    rv['Number of Local Annotations'] = len(graph.annotation_list)
    return rv
