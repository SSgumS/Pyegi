# -*- coding: utf-8 -*-
"""
Created on Fri May 23 13:38:34 2021

@author: saman
"""

from pyonfx import *
import Pyegi


io = Ass(Pyegi.GetInputFilePath(), extended=False)
meta, styles, lines = io.get_data()


def sub(line: Line, l: Line):  # ln: line number
    l.text = "{Pyegi}%s" % (line.raw_text)

    Pyegi.SendLine(l)


for line in lines[1:-1]:
    # Generating lines
    sub(line, line.copy())

for line in reversed(lines):
    # Generating lines
    sub(line, line.copy())


Pyegi.CreateOutputFile(original="C", placement="O")
