# -*- coding: utf-8 -*-
"""
Created on Fri May 23 13:38:34 2021

@author: saman
"""

from pyonfx import *
import sys

from pathlib import Path
file = Path(__file__).resolve()
sys.path.append(str(file.parents[2]) + "/Pyegi")
# TODO: I don't know shit about python packages; but this library should convert to an installable one. These path-play must not exist
import Pyegi


io = Ass(Pyegi.GetInputFilePath(), extended=False)
meta, styles, lines = io.get_data()


def sub(line: Line, l: Line):  # ln: line number
    l.text = "s1%s" % (line.raw_text)

    Pyegi.SendLine(l)


for line in lines[1:-1]:
    # Generating lines
    sub(line, line.copy())

for line in reversed(lines):
    # Generating lines
    sub(line, line.copy())


Pyegi.CreateOutputFile(original="C", placement="O")
