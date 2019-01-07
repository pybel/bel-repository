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
        name = 'egf.bel'

        with tempfile.TemporaryDirectory() as temporary_directory:
            bel_path = os.path.join(temporary_directory, name)
            to_bel_path(egf_graph, bel_path)

            r = BELRepository(temporary_directory)
            graphs = r.get_graphs()

            self.assertIn(bel_path, graphs)
            graph = graphs[bel_path]
            self.assertEqual(graph.document, egf_graph.document)
            self.assertEqual(set(graph.edges()), set(egf_graph.edges()))
            self.assertEqual(set(graph.edges()), set(egf_graph.edges()))

            self.assertTrue(os.path.exists(os.path.join(temporary_directory, f'{name}.json')))
            self.assertTrue(os.path.exists(os.path.join(temporary_directory, f'{name}.pickle')))


if __name__ == '__main__':
    unittest.main()
