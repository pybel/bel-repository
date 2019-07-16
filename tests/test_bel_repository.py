# -*- coding: utf-8 -*-

"""Tests for the repository class."""

import os
import tempfile
import unittest

from bel_repository import BELRepository
from pybel import to_bel_path
from pybel.examples import egf_graph
from pybel.testing.cases import TemporaryCacheMixin


class TestRepository(TemporaryCacheMixin):
    """Tests for the repository class."""

    def test_repository(self):
        """Test the repository class."""
        name = 'egf.bel'

        with tempfile.TemporaryDirectory() as temporary_directory:
            bel_path = os.path.join(temporary_directory, name)
            to_bel_path(egf_graph, bel_path)

            repository = BELRepository(temporary_directory)
            graphs = repository.get_graphs(
                manager=self.manager,
                use_cached=True,
                use_tqdm=False,
            )
            self.assertNotEqual(0, len(graphs), msg='No graphs returned')
            self.assertEqual(1, len(graphs))
            self.assertIn(bel_path, graphs)
            graph = graphs[bel_path]
            self.assertEqual(graph.document, egf_graph.document)
            self.assertEqual(set(graph.nodes()), set(egf_graph.nodes()))
            self.assertEqual(set(graph.edges()), set(egf_graph.edges()))

            self.assertTrue(os.path.exists(os.path.join(temporary_directory, f'{name}.json')))
            self.assertTrue(os.path.exists(os.path.join(temporary_directory, f'{name}.pickle')))


if __name__ == '__main__':
    unittest.main()
