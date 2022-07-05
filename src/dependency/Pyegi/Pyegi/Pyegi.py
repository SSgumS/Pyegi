import sys
from os.path import exists
import json
import numpy as np

output_data = [0]
auxiliary_output = {
    'Original Lines': 'C',  # 'C' for Commented, 'U' for Unchanged, and 'D' for deleted
}


def GetInputFilePath() -> str:
    return sys.argv[1]


def GetParameters():
    with open(sys.argv[3]) as file:
        parameters_table = json.load(file)
    return parameters_table


def AppendOutputFile(data: list[str]):
    data = ''.join(data[1:])
    file_name = sys.argv[2]
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(data)
        file.close()


def send_line(l):  # l: line table, ln: line number
    global output_data, auxiliary_output
    ln = l.i+1
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
        l.text
    )
    output_data.append(str_out)
    output_data[0] += len(str_out)
    if output_data[0] > 1000000:
        AppendOutputFile(output_data)
        output_data = [0]


def CreateOutputFile(original='C'):
    global output_data, auxiliary_output
    AppendOutputFile(output_data)
    output_data = [0]
    auxiliary_output['Original Lines'] = original
    file_name = sys.argv[5]
    json.dump(auxiliary_output, open(file_name, "w"))
