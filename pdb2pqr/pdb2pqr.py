"""TODO """

from .process_cli import process_cli


def main():
    """Hook for command-line usage."""
    args = process_cli()
    # read_input(args.input_file)
    # transform_data()
    # write_output()
