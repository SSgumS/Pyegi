"""

"""

from pyonfx import *
import math
import random
import sys

from pathlib import Path
file = Path(__file__).resolve()
sys.path.append(str(file.parents[2]) + "/Pyegi")
import Pyegi

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

io = Ass(Pyegi.GetInputFilePath())
meta, styles, lines = io.get_data()


def sub(line, l, ln): # ln: line number
    off = 20
    p_sh = Shape.rectangle()
    
    # Leadin Effect
    l.layer = 0

    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    l.text = "{\\an5\\move(%.3f,%.3f,%.3f,%.3f)\\bord0\\blur2\\t(0,%d,\\alpha&HFF&)}%s" % (
        line.center,
        line.middle,
        line.center+100,
        line.middle-30,
        max(min(5000, l.dur-2000),500),
        line.text,
    )
    
    send_line(l, ln)

    l.style = "Main - dummy"
    # Main Effect
    l.layer = 1

    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    for pixel in Convert.text_to_pixels(line):
        x, y = math.floor(line.left) + pixel.x, math.floor(line.top) + pixel.y
        x2, y2 = x + random.uniform(-off, off)+100, y + random.uniform(-off, off)-30
        alpha = (
            "\\alpha" + Convert.alpha_dec_to_ass(pixel.alpha)
            if pixel.alpha != 255
            else ""
        )

        l.text = "{\\p1\\move(%d,%d,%d,%d)%s\\fad(0,%d)}%s" % (
            x,
            y,
            x2,
            y2,
            alpha,
            l.dur / 4,
            p_sh,
        )
        send_line(l, ln)


for line in lines:
    # Generating lines
    sub(line, line.copy(), line.i+1)


Pyegi.CreateOutputFile(output_data)
