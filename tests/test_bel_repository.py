# -*- coding: utf-8 -*-

"""Tests for the repository class."""

import os
import tempfile
import unittest

from bel_repository import BELRepository
from pybel import to_bel_path
from pybel.examples import egf_graph


class TestRepository(unittest.TestCase):
    """Tests for the repository class."""

    def test_repository(self):
        """Test the repository class."""
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'efg.bel')
            to_bel_path(egf_graph, p)

            r = BELRepository(d)
            graphs = r.get_graphs()
            self.assertIn(p, graphs)
            graph = graphs[p]
            self.assertEqual(graph.document, egf_graph.document)
            self.assertEqual(set(graph.edges()), set(egf_graph.edges()))
            self.assertEqual(set(graph.edges()), set(egf_graph.edges()))


if __name__ == '__main__':
    unittest.main()
