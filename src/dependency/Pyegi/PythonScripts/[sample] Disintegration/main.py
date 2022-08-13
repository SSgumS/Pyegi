"""

"""

from pyonfx import *
import math
import random
import Pyegi


io = Ass(Pyegi.GetInputFilePath(), extended=True)
meta, styles, lines = io.get_data()


def sub(line, l):
    off = 20
    p_sh = Shape.rectangle()

    # Leadin Effect
    l.layer = 0

    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    l.text = (
        "{\\an5\\move(%.3f,%.3f,%.3f,%.3f)\\bord0\\blur2\\t(0,%d,\\alpha&HFF&)}%s"
        % (
            line.center,
            line.middle,
            line.center + 100,
            line.middle - 30,
            max(min(5000, l.dur - 2000), 500),
            line.text,
        )
    )

    Pyegi.SendLine(l)

    # Main Effect
    l.layer = 1

    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    for pixel in Convert.text_to_pixels(line):
        x, y = math.floor(line.left) + pixel.x, math.floor(line.top) + pixel.y
        x2, y2 = x + random.uniform(-off, off) + 100, y + random.uniform(-off, off) - 30
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
        Pyegi.SendLine(l)


for line in lines:
    # Generating lines
    sub(line, line.copy())


Pyegi.CreateOutputFile()
