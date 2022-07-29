import os
import json
import qdarktheme
from PyQt6.QtWidgets import QWidget
from enum import Enum

utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


class Theme(Enum):
    PYEGI = "Pyegi"
    DARK = "Dark"
    LIGHT = "Light"
    SYSTEM = "System Default"


def get_settings():
    f = open(settings_file_path)
    overall_settings = json.load(f)
    f.close()
    return overall_settings


def set_style(window: QWidget, theme: str = None):
    if not theme:
        # load theme
        overall_settings = get_settings()
        theme = overall_settings["Theme"]
    theme: Theme = Theme(theme)
    # set theme
    if theme == Theme.DARK:
        window.setStyleSheet(qdarktheme.load_stylesheet())
    elif theme == Theme.LIGHT:
        window.setStyleSheet(qdarktheme.load_stylesheet("light"))
    elif theme == Theme.SYSTEM:
        window.setStyleSheet("")
    else:
        f = open(f"{themes_path}{theme.value}.css", "r")
        theme_data = f.read()
        f.close()
        window.setStyleSheet(theme_data)
