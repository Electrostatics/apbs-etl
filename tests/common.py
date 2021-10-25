from pathlib import Path

DATA_DIR = Path(__file__).parent.absolute() / "data"
REF_DIR = DATA_DIR / "ref"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"


def get_ref_output(filename: str) -> str:
    with open(f"{REF_DIR}/{filename}", encoding="utf-8") as fin:
        return fin.read()
