import os
import sys
import pathlib

file = pathlib.Path(__file__).resolve()
sys.path.append(os.path.join(str(file.parents[2]), "Pyegi"))
