# Based on code from: https://www.geeksforgeeks.org/python-xml-to-json/
# Program to convert an xml file to a json file

from json import dumps
from pathlib import Path
from xmltodict import parse


def postprocessor(path, key, value):
    try:
        return key + ":float", float(value)
    except (ValueError, TypeError):
        try:
            return key + ":int", int(value)
        except (ValueError, TypeError):
            return key, value


def read_xml_write_json(filestem: str, suffix: str):
    # open the input xml file and read data in form of python dictionary using xmltodict module
    with open(f"{filestem}.{suffix}") as xml_file:
        data_dict = parse(xml_file.read(), postprocessor=postprocessor)

    # Write the json data to output json file
    with open(f"{filestem}.json", "w") as json_file:
        json_file.write(dumps(data_dict, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    path = Path(__file__).parent.resolve()

    xml_files = [path.stem for path in path.iterdir() if path.suffix in ".xml"]
    name_files = [
        path.stem for path in path.iterdir() if path.suffix in ".names"
    ]

    for file in sorted(xml_files):
        print(f"FILE: {file}")
        read_xml_write_json(str(file), "xml")
    for file in sorted(name_files):
        print(f"FILE: {file}")
        read_xml_write_json(str(file), "names")
