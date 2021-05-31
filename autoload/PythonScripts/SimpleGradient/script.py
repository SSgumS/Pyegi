# -*- coding: utf-8 -*-
"""
Created on Fri May 23 13:38:34 2021

@author: saman
"""

from pyonfx import *
import math
import numpy as np
import sys
import yaml

output_data = []

def send_line(l, ln): # l: line table, ln: line number
    global output_data
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
    output_data.insert(0, str_out)

# temp1 = 'C:/Users/saman/AppData/Roaming/Aegisub/automation/autoload/PythonScripts/'
io = Ass(sys.argv[1]+"InputSubtitle.ass")
# io = Ass(temp1+"InputSubtitle.ass")
meta, styles, lines = io.get_data()

def sub(line, l, ln): # ln: line number
    # Translation Effect
    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    # We define precision, increasing it will result in a gain on preformance and decrease of fidelity (due to less lines produced)
    precision = 10
    n = int(line.height / precision)

    for i in range(n):
        clip = "%d,%d,%d,%d" % (
            line.left,
            line.top + (line.height) * (i / n),
            line.right,
            line.top + (line.height) * ((i + 1) / n),
        )

        color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)

        l.text = "{\\an5\\pos(%.3f,%.3f)\\clip(%s)\\c%s}%s" % (
            line.center,
            line.middle,
            clip,
            color,
            line.text,
        )

        send_line(l, ln)


for line in lines:
    # Generating lines
    sub(line, line.copy(), line.i+1)


output_data = ''.join(output_data)
output_data = output_data[:-1]
# with open(temp1+'output.txt', 'w', encoding='utf-8') as output_file:
with open(sys.argv[1]+'output.txt', 'w', encoding='utf-8') as output_file:
    output_file.write(output_data)
    output_file.close()
