BEL Repository |build| |zenodo|
===============================
A utility for loading data from repositories of BEL documents with PyBEL [1]_.

Installation |pypi_version| |python_versions| |pypi_license|
------------------------------------------------------------
``bel_repository`` can be installed from PyPI with the following command:

.. code-block:: bash

   $ pip install bel-repository

The latest version can be installed from GitHub with:

.. code-block:: bash

   $ pip install git+https://github.com/pybel/bel-repository.git

Usage
-----
.. code-block:: python

    from typing import Mapping

    from bel_repository import BELRepository
    from pybel import BELGraph

    # Build a repository by giving a folder
    bel_repository = BELRepository('/path/to/folder/with/bel/')

    # Get a mapping from paths to graphs
    graphs: Mapping[str, BELGraph] = bel_repository.get_graphs()

    # Get a combine graph
    graph: BELGraph = bel_repository.get_graph()

Example BEL Repositories
------------------------
Each of these repositories has BEL content that can be pip installed:

- https://github.com/cthoyt/selventa-knowledge/
- https://github.com/pharmacome/conib
- https://github.com/hemekg/hemekg
- https://github.com/covid19kg/covid19kg
- https://github.com/neurommsig-epilepsy/neurommsig-epilepsy

More publicly available BEL content can be found in the listing in
`this blog post <https://cthoyt.com/2020/04/30/public-bel-content.html>`_.

References
----------
.. [1] Hoyt, C. T., *et al.* (2017). `PyBEL: a computational framework for Biological Expression
       Language <https://doi.org/10.1093/bioinformatics/btx660>`_. Bioinformatics (Oxford, England), 34(4), 703–704.

.. |build| image:: https://travis-ci.com/pybel/bel-repository.svg?branch=master
    :target: https://travis-ci.com/pybel/bel-repository

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/bel_repository.svg
    :alt: Stable Supported Python Versions

.. |pypi_version| image:: https://img.shields.io/pypi/v/bel_repository.svg
    :alt: Current version on PyPI

.. |pypi_license| image:: https://img.shields.io/pypi/l/bel_repository.svg
    :alt: License

.. |zenodo| image:: https://zenodo.org/badge/162814995.svg
   :target: https://zenodo.org/badge/latestdoi/162814995
