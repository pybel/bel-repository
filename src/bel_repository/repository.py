# -*- coding: utf-8 -*-

"""Utilities for BEL repositories."""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Set, TextIO, Tuple, Union

import click
import pandas as pd
from tqdm import tqdm

from pybel import BELGraph, Manager, from_path, union
from pybel.cli import connection_option
from .constants import IO_MAPPING, LOCAL_SUMMARY_EXT, OUTPUT_KWARGS
from .metadata import BELMetadata
from .utils import to_summary_json

__all__ = [
    'BELRepository',
    'append_click_group',
]

logger = logging.getLogger(__name__)


@dataclass
class BELRepository:
    """A container for a BEL repository."""

    directory: str
    output_directory: Optional[str] = None

    bel_cache_name: str = '_cache.bel'
    bel_metadata: Optional[BELMetadata] = None
    formats: Tuple[str, ...] = ('pickle', 'json', 'summary.json')

    #: Must include {file_name} and {extension}
    cache_fmt: str = '{file_name}.{extension}'
    global_summary_ext: str = 'summary.tsv'
    warnings_ext: str = 'warnings.tsv'

    @property
    def bel_summary_path(self) -> str:  # noqa: D401
        """The location where the summary DataFrame will be output as a TSV."""
        return self._build_cache_ext_path(
            root=self._cache_directory,
            file_name=self.bel_cache_name,
            extension=self.global_summary_ext.lstrip('.'),
        )

    @property
    def _cache_directory(self) -> str:  # noqa: D401
        """The output directory (defaults to input directory if not set)."""
        return self.output_directory or self.directory

    def _get_global_cache_path_by_extension(self, extension: str) -> str:
        return self._build_cache_ext_path(self._cache_directory, self.bel_cache_name, extension)

    def _build_cache_ext_path(self, root: str, file_name: str, extension: str) -> str:
        return os.path.join(root, self.cache_fmt.format(file_name=file_name, extension=extension.lstrip('.')))

    def _build_warnings_path(self, root: str, file_name: str) -> str:
        return self._build_cache_ext_path(root, file_name, self.warnings_ext.lstrip('.'))

    def _build_summary_path(self, root: str, file_name: str) -> str:
        return self._build_cache_ext_path(root, file_name, LOCAL_SUMMARY_EXT)

    def walk(self) -> Iterable[Tuple[str, Iterable[str], Iterable[str]]]:
        """Recursively walk this directory."""
        return os.walk(self.directory)

    def iterate_bel(self) -> Iterable[Tuple[str, str]]:
        """Yield all paths to BEL documents."""
        for root, dirs, file_names in self.walk():
            for file_name in sorted(file_names):
                if not file_name.startswith('_') and file_name.endswith('.bel'):
                    yield root, file_name

    def clear_global_cache(self) -> None:
        """Clear the global cache."""
        self._remove_root_file_name(self._cache_directory, self.bel_cache_name)

    def clear_local_caches(self) -> None:
        """Clear all caches of BEL documents in the repository."""
        for root, file_name in self.iterate_bel():
            self._remove_root_file_name(root, file_name)

    def _remove_root_file_name(self, root: str, file_name: str) -> None:
        for extension, path in self._iterate_extension_path(root, file_name):
            if os.path.exists(path):
                os.remove(path)

    def _iterate_extension_path(self, root: str, file_name: str) -> Iterable[Tuple[str, str]]:
        for extension in self.formats:
            yield extension, self._build_cache_ext_path(root, file_name, extension)

    def _import_local(self, root: str, file_name: str) -> Optional[BELGraph]:
        for extension, path in self._iterate_extension_path(root, file_name):
            _, importer = IO_MAPPING[extension]
            if importer is not None and os.path.exists(path):
                return importer(path)

        return None

    def _import_global(self) -> Optional[BELGraph]:
        return self._import_local(self._cache_directory, self.bel_cache_name)

    def _export_local(self, graph: BELGraph, root: str, file_name: str) -> None:
        for extension, path in self._iterate_extension_path(root, file_name):
            exporter, _ = IO_MAPPING[extension]
            kwargs = OUTPUT_KWARGS.get(extension, {})
            exporter(graph, path, **kwargs)

        if graph.warnings:
            logger.info(f' - {graph.number_of_warnings()} warnings')
            warnings_path = self._build_warnings_path(root, file_name)
            warnings_df = pd.DataFrame([
                (exc.line_number, exc.position, exc.line, exc.__class__.__name__, str(exc))
                for _, exc, _ in graph.warnings
            ], columns=['Line Number', 'Position', 'Line', 'Error', 'Message'])
            warnings_df.to_csv(warnings_path, sep='\t', index=False)

    def _export_global(self, graph: BELGraph) -> None:
        self._export_local(graph, self._cache_directory, self.bel_cache_name)

    def get_graph(self,
                  manager: Optional[Manager] = None,
                  use_cached: bool = False,
                  use_tqdm: bool = False,
                  tqdm_kwargs: Optional[Mapping[str, Any]] = None,
                  from_path_kwargs: Optional[Mapping[str, Any]] = None,
                  ) -> BELGraph:
        """Get a combine graph."""
        if use_cached:
            graph = self._import_global()
            if graph is not None:
                return graph

        graphs = self.get_graphs(
            manager=manager,
            use_tqdm=use_tqdm,
            tqdm_kwargs=tqdm_kwargs,
            from_path_kwargs=from_path_kwargs,
        )
        graph = union(graphs.values())

        if self.bel_metadata is not None:
            self.bel_metadata.update(graph)

        self._get_summary_df_from_graphs(graphs)
        self._export_global(graph)

        return graph

    def get_graphs(self,
                   manager: Optional[Manager] = None,
                   use_cached: bool = False,
                   use_tqdm: bool = False,
                   tqdm_kwargs: Optional[Mapping[str, Any]] = None,
                   from_path_kwargs: Optional[Mapping[str, Any]] = None,
                   ) -> Mapping[str, BELGraph]:
        """Get a mapping of all graphs' paths to their compiled BEL graphs."""
        if manager is None:
            manager = Manager()

        paths = self.iterate_bel()
        if use_tqdm:
            paths = tqdm(list(paths), **(tqdm_kwargs or {}))

        rv = {}
        for root, file_name in paths:
            path = os.path.join(root, file_name)

            if use_cached:
                graph = self._import_local(root, file_name)
                if graph is not None:
                    rv[path] = graph
                    continue

            try:
                graph = rv[path] = from_path(path, manager=manager, **(from_path_kwargs or {}))
            except Exception:
                logger.warning(f'problem with {graph}')
                continue

            self._export_local(graph, root, file_name)

        return rv

    def get_summary_df(self,
                       manager: Optional[Manager] = None,
                       use_cached: bool = False,
                       use_tqdm: bool = False,
                       tqdm_kwargs: Optional[Mapping[str, Any]] = None,
                       from_path_kwargs: Optional[Mapping[str, Any]] = None,
                       save: Union[bool, str, TextIO] = True,
                       ) -> pd.DataFrame:
        """Get a pandas DataFrame summarizing the contents of all graphs in the repository."""
        graphs = self.get_graphs(
            manager=manager,
            use_cached=use_cached,
            use_tqdm=use_tqdm,
            tqdm_kwargs=tqdm_kwargs,
            from_path_kwargs=from_path_kwargs,
        )
        return self._get_summary_df_from_graphs(graphs, save=save)

    def _get_summary_df_from_graphs(self, graphs, save: Union[str, bool, TextIO] = True):
        summary_dicts = {
            os.path.relpath(path, self.directory): to_summary_json(graph)
            for path, graph in graphs.items()
        }

        df = pd.DataFrame.from_dict(summary_dicts, orient='index')

        if isinstance(save, str):
            df.to_csv(save, sep='\t')
        elif save:
            df.to_csv(self.bel_summary_path, sep='\t')

        return df

    def build_cli(self):  # noqa: D202
        """Build a command line interface."""

        @click.group(help=f'Tools for the BEL repository at {self.directory}')
        @click.pass_context
        def main(ctx):
            """Group the commands."""
            ctx.obj = self

        append_click_group(main)
        return main

    def get_extensions(self, root: str, file_name: str) -> Set[str]:
        """Get all compiled files for the given BEL."""
        # TODO check that this is a valid BEL path!
        return {
            extension
            for extension, path in self._iterate_extension_path(root, file_name)
            if os.path.exists(path)
        }

    def _get_global_caches(self):
        return self.get_extensions(self._cache_directory, self.bel_cache_name)


def append_click_group(main: click.Group) -> None:  # noqa: D202, C901
    """Append a :py:class:`click.Group`."""

    @main.command()
    @click.pass_obj
    def ls(bel_repository: BELRepository):
        """List the contents of the repository."""
        global_caches = bel_repository._get_global_caches()
        if global_caches:
            click.secho('Global Cache', fg='red', bold=True)
            _write_caches(bel_repository, bel_repository._cache_directory, bel_repository.bel_cache_name)
            click.secho('Local Caches', fg='red', bold=True)

        for root, file_name in bel_repository.iterate_bel():
            _write_caches(bel_repository, root, file_name)

    def _write_caches(bel_repository, root: str, file_name: str):
        extensions = ', '.join(sorted(bel_repository.get_extensions(root, file_name)))
        has_warnings = os.path.exists(bel_repository._build_warnings_path(root, file_name))

        try:
            with open(bel_repository._build_summary_path(root, file_name)) as file:
                summary = json.load(file)
        except FileNotFoundError:
            summary = None

        if extensions and has_warnings:
            s = click.style('✘️ ', fg='red')
        elif extensions and not has_warnings:
            s = click.style('✔︎ ', fg='green')
        else:
            s = click.style('? ', fg='yellow', bold=True)

        path = os.path.join(root, file_name)
        s += os.path.relpath(path, bel_repository.directory)

        if extensions:
            s += click.style(f' ({extensions})', fg='green')

        if summary:
            s += click.style(f' ({summary["Number of Nodes"]} nodes, {summary["Number of Edges"]} edges)', fg='blue')

        click.echo(s)

    @main.command()
    @click.confirmation_option()
    @click.pass_obj
    def uncache(bel_repository: BELRepository):
        """Clear the cached data for the repository."""
        bel_repository.clear_global_cache()
        bel_repository.clear_local_caches()

    @main.command()
    @click.confirmation_option()
    @click.pass_obj
    def uncache_global(bel_repository: BELRepository):
        """Clear the cached data for the repository."""
        bel_repository.clear_global_cache()

    @main.command()
    @click.confirmation_option()
    @click.pass_obj
    def uncache_local(bel_repository: BELRepository):
        """Clear the cached data for the repository."""
        bel_repository.clear_local_caches()

    @main.command()
    @connection_option
    @click.option('--reload', is_flag=True)
    @click.option('--no-tqdm', is_flag=True)
    @click.pass_obj
    def compile(bel_repository: BELRepository, connection: str, reload: bool, no_tqdm: bool):
        """Summarize the repository."""
        if reload:
            bel_repository.clear_global_cache()
            bel_repository.clear_local_caches()

        manager = Manager(connection=connection)
        graph = bel_repository.get_graph(
            manager=manager,
            use_cached=(not reload),
            use_tqdm=(not no_tqdm),
            tqdm_kwargs=dict(
                desc='Loading BEL',
                leave=False,
            ),
            from_path_kwargs=dict(
                use_tqdm=(not no_tqdm),
                tqdm_kwargs=dict(
                    leave=False,
                ),
            ),
        )
        click.echo(graph.summary_str())
