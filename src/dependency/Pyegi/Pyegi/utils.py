import os
import json
import qdarktheme

utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


def set_style(self, Window, origin="settings file"):
    if origin == "settings file":
        f = open(settings_file_path)
        self.overall_settings = json.load(f)
        f.close()
        theme_name = self.overall_settings["Theme"]
    elif origin == "combobox":
        theme_name = self.themes_combobox.currentText()
    if theme_name == "Dark":
        Window.setStyleSheet(qdarktheme.load_stylesheet())
    elif theme_name == "Light":
        Window.setStyleSheet(qdarktheme.load_stylesheet("light"))
    elif theme_name == "Default":
        Window.setStyleSheet("")
    else:
        f = open(f"{themes_path}{theme_name}.css", "r")
        theme_data = f.read()
        f.close()
        Window.setStyleSheet(theme_data)
    return self
