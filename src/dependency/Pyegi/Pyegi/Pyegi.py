import sys
import json
import typing
from minimals.minimal_pkg_installer import write_json

if typing.TYPE_CHECKING:
    from pyonfx import Line


ـoutput_size = 0
ـoutput_data = []
ـauxiliary_output = {
    "Original Lines": "C",  # 'C' for Commented, 'U' for Unchanged, and 'D' for deleted
    "Placement": "O",  # 'O' for below Original, 'E' for End, and 'S' for Start
}


def GetInputFilePath() -> str:
    return sys.argv[1]


def GetOutputFilePath() -> str:
    return sys.argv[2]


def GetParameters():
    with open(sys.argv[3]) as file:
        parameters_table = json.load(file)
    return parameters_table


def GetScriptName() -> str:
    return sys.argv[4]


def GetAuxiliaryFilePath() -> str:
    return sys.argv[5]


def GetProjectPropertiesFilePath() -> str:
    return sys.argv[6]


def AppendOutputFile(data: list[str]):
    global ـoutput_size, ـoutput_data
    dataString = "".join(data)
    file_name = GetOutputFilePath()
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(dataString)
        file.close()
    # reset output data
    ـoutput_size = 0
    ـoutput_data = []


def SendLine(l: "Line"):  # l: line table, ln: line number
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
        AppendOutputFile(ـoutput_data)


def CreateOutputFile(original="C", placement="O"):
    # original choices:
    # 'C': the original lines in the subtitle file will be Commented
    # 'D': the original lines in the subtitle file will be Deleted
    # 'U': the original lines in the subtitle file won't be modified
    # placement choices:
    # 'O': produced line(s) will be placed below the corresponding Original line
    # 'E': produced line(s) will be placed at the end of subtitle file
    # 'S': produced line(s) will be placed at the start of subtitle file
    global ـoutput_data, ـauxiliary_output
    AppendOutputFile(ـoutput_data)
    ـauxiliary_output["Original Lines"] = original
    ـauxiliary_output["Placement"] = placement
    file_name = GetAuxiliaryFilePath()
    write_json(ـauxiliary_output, file_name)
