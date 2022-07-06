import sys
from os.path import exists
import json
import numpy as np
from pyonfx import Line

output_data = [0]
auxiliary_output = {
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


def AppendOutputFile(data: list[str]):
    data = "".join(data[1:])
    file_name = GetOutputFilePath()
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(data)
        file.close()


def SendLine(l: Line):  # l: line table, ln: line number
    global output_data, auxiliary_output
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
    output_data.append(str_out)
    output_data[0] += len(str_out)
    if output_data[0] > 1000000:
        AppendOutputFile(output_data)
        output_data = [0]


def CreateOutputFile(original="C", placement="O"):
    # original choices:
    # 'C': the original lines in the subtitle file will be Commented
    # 'D': the original lines in the subtitle file will be Deleted
    # 'U': the original lines in the subtitle file won't be modified
    # placement choices:
    # 'O': produced line(s) will be placed below the corresponding Original line
    # 'E': produced line(s) will be placed at the end of subtitle file
    # 'S': produced line(s) will be placed at the start of subtitle file
    global output_data, auxiliary_output
    AppendOutputFile(output_data)
    output_data = [0]
    auxiliary_output["Original Lines"] = original
    auxiliary_output["Placement"] = placement
    file_name = GetAuxiliaryFilePath()
    json.dump(auxiliary_output, open(file_name, "w"))
