import sys
from os.path import exists
import json
import numpy as np

output_data = [0]
auxiliary_output = {
    'Original Lines': 'C',  # 'C' for Commented, 'U' for Unchanged, and 'D' for deleted
    'Produced Lines': [],
    'Produced Lines_cs': []  # cumsum
}
corresponding_lines = []


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
    global output_data, auxiliary_output, corresponding_lines
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
    if ln in corresponding_lines:
        auxiliary_output['Produced Lines'][corresponding_lines.index(ln)] += 1
    else:
        corresponding_lines.append(ln)
        auxiliary_output['Produced Lines'].append(1)
    output_data.append(str_out)
    output_data[0] += len(str_out)
    if output_data[0] > 1000000:
        AppendOutputFile(output_data)
        output_data = [0]


def CreateOutputFile(original='C'):
    global output_data, auxiliary_output, corresponding_lines
    AppendOutputFile(output_data)
    output_data = [0]
    auxiliary_output['Original Lines'] = original
    if original == 'D':
        auxiliary_output['Produced Lines_cs'] = np.cumsum(
            np.array(auxiliary_output['Produced Lines'])-1).tolist()
    else:
        auxiliary_output['Produced Lines_cs'] = np.cumsum(
            np.array(auxiliary_output['Produced Lines'])).tolist()
    file_name = sys.argv[5]
    json.dump(auxiliary_output, open(file_name, "w"))
