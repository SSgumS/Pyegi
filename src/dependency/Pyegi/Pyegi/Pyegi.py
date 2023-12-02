import sys
import json
import typing
from minimals.minimal_pkg_installer import write_json
from enum import Enum

if typing.TYPE_CHECKING:
    from pyonfx import Line

class Transform(Enum):
    COMMENTED = "Commented"
    UNCHANGED = "Unchanged"
    DELETED = "Deleted"

class Location(Enum):
    BELOW = "Below Original"
    END = "End"
    START = "Start"

ـoutput_size = 0
ـoutput_data = []
ـauxiliary_output = {
    "Original Lines": Transform.COMMENTED,
    "Placement": Location.BELOW,
}


def get_input_file_path() -> str:
    """Returns the path for the subtitle created by Pyegi (lua section) based on the current state of the working subtitle.
    """
    return sys.argv[1]


def get_output_file_path() -> str:
    """Returns the path for the output file to save the output of the python script in a certain format to be inserted in the working subtitle.
    """
    return sys.argv[2]


def get_parameters():
    """Loads the contents of the file containing the current states of the script GUI variables to a table.
    """
    with open(sys.argv[3]) as file:
        parameters_table = json.load(file)
    return parameters_table


def get_script_name() -> str:
    """Returns the name of the selected script.
    """
    return sys.argv[4]


def get_auxiliary_file_path() -> str:
    """Returns the path for the file which contains the directions for inserting the new subtitle line(s) as well as modifying the original line(s) in the working subtitle.
    """
    return sys.argv[5]


def get_project_properties():
    """Loads the contents of the file containing the properties of the working subtitle (like video_position, active_row, etc) to a table.
    """
    with open(sys.argv[6]) as file:
        project_properties = json.load(file)
    return project_properties


def append_output_file(data: list[str]):
    """Appends the new data to the output file.
    """
    global ـoutput_size, ـoutput_data
    dataString = "".join(data)
    file_name = get_output_file_path()
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(dataString)
        file.close()
    # reset output data
    ـoutput_size = 0
    ـoutput_data = []


def send_line(l: "Line"):  # l: line table, ln: line number
    """Converts the subtitle line to a string with a certain formatting and appends it to a list containing the previously created strings of this sort.
    """
    global ـoutput_size, ـoutput_data, ـauxiliary_output
    ln = l.i + 1
    str_out = "%d\n%d\n%d\n%d\n%s\n%s\n%d\n%d\n%d\n%s\n%s\n" % (
        ln,
        l.layer,
        l.start_time,
        l.end_time,
        l.style,
        l.actor,
        l.margin_l,
        l.margin_r,
        l.margin_v,
        l.effect,
        l.text,
    )
    ـoutput_data.append(str_out)
    ـoutput_size += len(str_out)
    if ـoutput_size > 1000000:
        append_output_file(ـoutput_data)


def create_output_file(transform_original=Transform.COMMENTED, insert_new=Location.BELOW):
    """Writes the data (or the remaining of the data) to the output file.
    """
    # transform_original choices:
    # 'Commented': the original lines in the subtitle file will be Commented
    # 'Deleted': the original lines in the subtitle file will be Deleted
    # 'Unchanged': the original lines in the subtitle file won't be modified
    # insert_new choices:
    # 'Below Original': produced line(s) will be placed below the corresponding Original line
    # 'End': produced line(s) will be placed at the end of subtitle file
    # 'Start': produced line(s) will be placed at the start of subtitle file
    global ـoutput_data, ـauxiliary_output
    append_output_file(ـoutput_data)
    ـauxiliary_output["Original Lines"] = transform_original.value
    ـauxiliary_output["Placement"] = insert_new.value
    file_name = get_auxiliary_file_path()
    write_json(ـauxiliary_output, file_name)
