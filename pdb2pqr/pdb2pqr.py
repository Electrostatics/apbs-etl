"""TODO """

from typing import List

from pdbx.containers import DataContainer

from .io import read_input
from .process_cli import process_cli


def main():
    """Hook for command-line usage."""
    args = process_cli()
    data_containers: List[DataContainer] = read_input(args.input_file)
    # transform_data()
    # write_output()
