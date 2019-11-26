# -*- coding: utf-8 -*-

"""Constants for BEL repositories."""

from pybel import (
    from_cx_file, from_cx_gz, from_jgif_file, from_jgif_gz, from_nodelink_file, from_nodelink_gz, from_pickle,
    to_cx_file, to_cx_gz, to_jgif_file, to_jgif_gz, to_nodelink_file, to_nodelink_gz, to_pickle,
)
from .utils import to_summary_json_path

__all__ = [
    'IO_MAPPING',
    'OUTPUT_KWARGS',
    'LOCAL_SUMMARY_EXT',
]

LOCAL_SUMMARY_EXT = 'summary.json'

IO_MAPPING = {
    'pickle': (to_pickle, from_pickle),
    'nodelink.json': (to_nodelink_file, from_nodelink_file),
    'nodelink.json.gz': (to_nodelink_gz, from_nodelink_gz),
    'cx.json': (to_cx_file, from_cx_file),
    'cx.json.gz': (to_cx_gz, from_cx_gz),
    'jgif.json': (to_jgif_file, from_jgif_file),
    'jgif.json.gz': (to_jgif_gz, from_jgif_gz),
    LOCAL_SUMMARY_EXT: (to_summary_json_path, None),
}

OUTPUT_KWARGS = {
    'nodelink.json': dict(indent=2, sort_keys=True),
    'cx.json': dict(indent=2, sort_keys=True),
    'jgif.json': dict(indent=2, sort_keys=True),
}
