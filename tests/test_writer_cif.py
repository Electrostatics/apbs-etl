"""This file tests the CIF writer."""
from typing import List
import pytest
from pathlib import Path
from pdbx import DataContainer, DataCategory
from pdbx.writer import PdbxWriter

CONTAINER = DataContainer("junk")


def test_write_data_file(tmp_path):
    """Test case -  write data file."""
    output_path = Path(tmp_path) / Path("test-output.cif")
    category = DataCategory("pdbx_seqtool_mapping_ref")
    category.append_attribute("ordinal")
    category.append_attribute("entity_id")
    category.append_attribute("auth_mon_id")
    category.append_attribute("auth_mon_num")
    category.append_attribute("pdb_chain_id")
    category.append_attribute("ref_mon_id")
    category.append_attribute("ref_mon_num")
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    container = DataContainer("myblock")
    container.append(category)
    data_list = [container]
    with open(output_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(data_list)

    print(f"Output written to: {output_path}")


@pytest.mark.parametrize(
    "category_name, attribute_list, data",
    [
        pytest.param(
            "pdbx_seqtool_mapping_ref",
            [
                "ordinal",
                "entity_id",
                "auth_mon_id",
                "auth_mon_num",
                "pdb_chain_id",
                "ref_mon_id",
                "ref_mon_num",
            ],
            [
                (1, 2, 3, 4, 5, 6, 7),
                (1, 2, 3, 4, 5, 6, 7),
                (1, 2, 3, 4, 5, 6, 7),
                (1, 2, 3, 4, 5, 6, 7),
            ],
            id="1",
        ),
        pytest.param(
            "JUNK",
            [
                "ordinal",
                "entity_id",
                "auth_mon_id",
                "auth_mon_num",
                "pdb_chain_id",
                "ref_mon_id",
                "ref_mon_num",
            ],
            [(1, 2, 3, 4, 5, 6, 7)],
            id="2",
        ),
    ],
)
def test_write_data_file2(
    tmp_path, category_name: str, attribute_list: List[str], data: List[tuple]
):
    """Test case -  write data file."""
    output_path = Path(tmp_path) / Path("test-output2.cif")
    category = DataCategory(category_name)

    for attribute in attribute_list:
        category.append_attribute(attribute)

    for item in data:
        print(item)
        category.append(item)

    CONTAINER.append(category)
    data_list = [CONTAINER]
    with open(output_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(data_list)

    print(f"Output written to: {output_path}")

    # dict {
    #     'ATOM': [[1st atom data]], [2nd atom data]],
    #     'REMARK': [[1st remark]],
    # }
