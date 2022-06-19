import sys
import json

def GetInputFilePath() -> str:
    return sys.argv[1]

def GetParameters():
    with open(sys.argv[3]) as file:
        parameters_table = json.load(file)
    return parameters_table

def CreateOutputFile(data: list[str]):
    data = ''.join(data)
    data = data[:-1]
    with open(sys.argv[2], 'w', encoding='utf-8') as file:
        file.write(data)
        file.close()