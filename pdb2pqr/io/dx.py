from io import FileIO


def read_dx(dx_file: FileIO):
    """Read DX-format volumetric information.

    The OpenDX file format is defined at
    <https://www.idvbook.com/wp-content/uploads/2010/12/opendx.pdf`.

    .. note:: This function is not a general-format OpenDX file parser and
       makes many assumptions about the input data type, grid structure, etc.

    .. todo:: This function should be moved into the APBS code base.

    :param dx_file:  file object for DX file, ready for reading as text
    :type dx_file:  file
    :returns:  dictionary with data from DX file
    :rtype:  dict
    :raises ValueError:  on parsing error
    """
    dx_dict = {
        "grid spacing": [],
        "values": [],
        "number of grid points": None,
        "lower left corner": None,
    }
    for line in dx_file:
        words = [w.strip() for w in line.split()]
        if words[0] in ["#", "attribute", "component"]:
            pass
        elif words[0] == "object":
            if words[1] == "1":
                dx_dict["number of grid points"] = (
                    int(words[5]),
                    int(words[6]),
                    int(words[7]),
                )
        elif words[0] == "origin":
            dx_dict["lower left corner"] = [
                float(words[1]),
                float(words[2]),
                float(words[3]),
            ]
        elif words[0] == "delta":
            spacing = [float(words[1]), float(words[2]), float(words[3])]
            dx_dict["grid spacing"].append(spacing)
        else:
            for word in words:
                dx_dict["values"].append(float(word))
    return dx_dict


def write_cube(cube_file: FileIO, data_dict: dict, atom_list: list, comment:str="CPMD CUBE FILE."):
    """Write a Cube-format data file.

    Cube file format is defined at
    <https://docs.chemaxon.com/display/Gaussian_Cube_format.html>.

    .. todo:: This function should be moved into the APBS code base.

    :param cube_file:  file object ready for writing text data
    :type cube_file:  file
    :param data_dict:  dictionary of volumetric data as produced by
        :func:`read_dx`
    :type data_dict:  dict
    :param comment:  comment for Cube file
    :type comment:  str
    """
    cube_file.write(f"{comment}\n")
    cube_file.write("OUTER LOOP: X, MIDDLE LOOP: Y, INNER LOOP: Z\n")
    num_atoms = len(atom_list)
    origin = data_dict["lower left corner"]
    cube_file.write(
        f"{num_atoms:>4} {origin[0]:>11.6f} {origin[1]:>11.6f} "
        f"{origin[2]:>11.6f}\n"
    )
    num_points = data_dict["number of grid points"]
    spacings = data_dict["grid spacing"]
    for i in range(3):
        cube_file.write(
            f"{-num_points[i]:>4} "
            f"{spacings[i][0]:>11.6f} "
            f"{spacings[i][1]:>11.6f} "
            f"{spacings[i][2]:>11.6f}\n"
        )
    for atom in atom_list:
        cube_file.write(
            f"{atom.serial:>4} {atom.charge:>11.6f} {atom.x:>11.6f} "
            f"{atom.y:>11.6f} {atom.z:>11.6f}\n"
        )
    stride = 6
    values = data_dict["values"]
    for i in range(0, len(values), 6):
        if i + stride < len(values):
            imax = i + 6
            words = [f"{val:< 13.5E}" for val in values[i:imax]]
            cube_file.write(" ".join(words) + "\n")
        else:
            words = [f"{val:< 13.5E}" for val in values[i:]]
            cube_file.write(" ".join(words))
