# -*- coding: utf-8 -*-
"""
Created on Fri May 23 13:38:34 2021

@author: saman
"""

from pyonfx import *
import numpy as np
import sys

from pathlib import Path
file = Path(__file__).resolve()
sys.path.append(str(file.parents[2]) + "/Pyegi")
import Pyegi # TODO: I don't know shit about python packages; but this library should convert to an installable one. These path-play must not exist
# from .. .. Pyegi import Pyegi # this is for having intellisense in development

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

parameters_table = Pyegi.GetParameters()
for items in parameters_table['Controls']:
    if items['name'] == 'dropdown1':
        direction1 = items['value']
    if items['name'] == 'floatedit1':
        angle1 = items['value']%180
if direction1 == 'Slant':
    if angle1 == 0:
        direction1 = 'Vertical'
    if angle1 == 90:
        direction1 = 'Horizontal'

io = Ass(Pyegi.GetInputFilePath())
meta, styles, lines = io.get_data()

# oval specs
os1 = .436
os1p = 1.+os1
os2 = .689
os2p = 1.+os2

def sub(line, l, ln): # ln: line number
    # Translation Effect
    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    w1 = line.width
    # w1 = 300
    h1 = line.height
    # h1 = 200

    # We define precision, increasing it will result in a gain on preformance and decrease of fidelity (due to less lines produced)
    precision = 20
    if direction1 == 'Horizontal':
        n = int(w1 / precision)
    elif direction1 == 'Vertical':
        n = int(h1 / precision)
    elif direction1 == 'Slant':
        sin1 = np.sin(np.deg2rad(angle1))
        cos1 = np.cos(np.deg2rad(angle1))
        h2 = w1*sin1 + abs(h1*cos1)
        n = int(h2 / precision)
    elif direction1 == 'Oval':
        n = int(max(h1,w1) / precision)

    if direction1 == 'Horizontal':
        for i in range(n):
            clip = "%.2f,%.2f,%.2f,%.2f" % (
                line.right - w1 * ((i + 1) / n),
                line.top,
                line.right - w1 * (i / n),
                line.bottom,
            )
    
            color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)
    
            l.text = "{\\an5\\pos(%.2f,%.2f)\\clip(%s)\\c%s}%s" % (
                line.center,
                line.middle,
                clip,
                color,
                line.raw_text,
            )
    
            send_line(l, ln)
            
    if direction1 == 'Vertical':
        for i in range(n):
            clip = "%.2f,%.2f,%.2f,%.2f" % (
                line.left,
                line.bottom - h1 * ((i + 1) / n),
                line.right,
                line.bottom - h1 * (i / n),
            )
    
            color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)
    
            l.text = "{\\an5\\pos(%.2f,%.2f)\\clip(%s)\\c%s}%s" % (
                line.center,
                line.middle,
                clip,
                color,
                line.raw_text,
            )
    
            send_line(l, ln)
            
    if direction1 == 'Slant':
        eps1 = 1.
        if angle1 < 90:
            for i in range(n):
                clip = "m %.2f %.2f l %.2f %.2f %.2f %.2f %.2f %.2f" % (
                    line.right - w1*cos1**2 - h2*(i/n)*sin1,
                    line.bottom + w1*sin1*cos1 - h2*(i/n)*cos1,
                    line.right + h1*sin1*cos1 - h2*(i/n)*sin1,
                    line.bottom - h1*sin1**2 - h2*(i/n)*cos1,
                    line.right + h1*sin1*cos1 - h2*((i+1)/n)*sin1 - eps1,
                    line.bottom - h1*sin1**2 - h2*((i+1)/n)*cos1 - eps1,
                    line.right - w1*cos1**2 - h2*((i+1)/n)*sin1 - eps1,
                    line.bottom + w1*sin1*cos1 - h2*((i+1)/n)*cos1 - eps1,
                )
        
                color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)
        
                l.text = "{\\an5\\pos(%.2f,%.2f)\\clip(%s)\\bord0\\shad0\\c%s}%s" % (
                    line.center,
                    line.middle,
                    clip,
                    color,
                    line.raw_text,
                )
        
                send_line(l, ln)
                
        else:
            for i in range(n):
                clip = "m %.2f %.2f l %.2f %.2f %.2f %.2f %.2f %.2f" % (
                    line.right - h1*sin1*cos1 - h2*(i/n)*sin1,
                    line.top + h1*sin1**2 - h2*(i/n)*cos1,
                    line.right - w1*cos1**2 - h2*(i/n)*sin1,
                    line.top + w1*sin1*cos1 - h2*(i/n)*cos1,
                    line.right - w1*cos1**2 - h2*((i+1)/n)*sin1 - eps1,
                    line.top + w1*sin1*cos1 - h2*((i+1)/n)*cos1 + eps1,
                    line.right - h1*sin1*cos1 - h2*((i+1)/n)*sin1 - eps1,
                    line.top + h1*sin1**2 - h2*((i+1)/n)*cos1 + eps1,
                )
        
                color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)
        
                l.text = "{\\an5\\pos(%.2f,%.2f)\\clip(%s)\\bord0\\shad0\\c%s}%s" % (
                    line.center,
                    line.middle,
                    clip,
                    color,
                    line.raw_text,
                )
        
                send_line(l, ln)
        
    if direction1 == 'Oval':
        for i in range(n):
            # m 50 0 b 117 0 117 100 50 100 -17 100 -17 0 50 0
            clip = "m %.2f %.2f b %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f" % (
                line.center,
                line.top - os1*h1/2 + (os1p*h1/2)*(i/n),
                line.right + os2*w1/2 - (os2p*w1/2)*(i/n),
                line.top - os1*h1/2 + (os1p*h1/2)*(i/n),
                line.right + os2*w1/2 - (os2p*w1/2)*(i/n),
                line.bottom + os1*h1/2 - (os1p*h1/2)*(i/n),
                line.center,
                line.bottom + os1*h1/2 - (os1p*h1/2)*(i/n),
                line.left - os2*w1/2 + (os2p*w1/2)*(i/n),
                line.bottom + os1*h1/2 - (os1p*h1/2)*(i/n),
                line.left - os2*w1/2 + (os2p*w1/2)*(i/n),
                line.top - os1*h1/2 + (os1p*h1/2)*(i/n),
                line.center,
                line.top - os1*h1/2 + (os1p*h1/2)*(i/n),
            )
    
            color = Utils.interpolate(i / n, "&H00FFF7&", "&H0000FF&", 1.4)
    
            l.text = "{\\an5\\pos(%.2f,%.2f)\\clip(%s)\\bord0\\shad0\\c%s}%s" % (
                line.center,
                line.middle,
                clip,
                color,
                line.raw_text,
            )
    
            send_line(l, ln)


for line in lines:
    # Generating lines
    sub(line, line.copy(), line.i+1)


Pyegi.CreateOutputFile(output_data)
