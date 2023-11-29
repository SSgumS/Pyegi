from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QColorDialog,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import QCoreApplication, QLocale
import os
from os.path import exists
import json
import sys
import numpy as np
from utils import set_style, GLOBAL_PATHS, FeedFile, write_json


system_inputs = sys.argv


def exec2(self, string):
    try:
        return exec(string)
    except:
        pass

QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

class Ui_LuaConverter(object):
    def setupUi(self, LuaConverter, script_id, window_name="main_window"):
        LuaConverter.setObjectName("LuaConverter")
        set_style(LuaConverter)

        self.centralwidget = QtWidgets.QWidget(LuaConverter)
        self.centralwidget.setObjectName("centralwidget")

        self.window_layout = QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.widgets_layout.setContentsMargins(20, 20, 20, 0)
        self.widgets_layout.setVerticalSpacing(10)

        # get script details
        self.script = FeedFile().get_script(script_id)

        if exists(system_inputs[3]):
            script_settings_file_path = system_inputs[3]
        else:
            script_settings_file_path = (
                self.script.folder + GLOBAL_PATHS.settings_filename
            )

        with open(script_settings_file_path) as file:
            script_settings = json.load(file)

        for i, w in enumerate(script_settings["Windows"]):
            if w["name"] == window_name:
                widgets = w
                window_index = i

        defW = 120  # default width
        defH = 25  # default height
        offX = 20  # offset in the X axis direction
        offY = 25  # offset in the Y axis direction
        Wfinal = 0  # final width of the window
        Hfinal = 0  # final height of the window
        lua_pyqt_conversion = {
            "label": "QLabel",
            "edit": "QLineEdit",
            "intedit": "QSpinBox",
            "floatedit": "QDoubleSpinBox",
            "textbox": "QTextEdit",
            "dropdown": "QComboBox",
            "checkbox": "QCheckBox",
            "color": "QPushButton",
            "coloralpha": "QPushButton",
            "alpha": "QLineEdit",
            "Pyegi_button": "QPushButton",
        }
        max_row_col = 100
        widgets_map = np.zeros((max_row_col, max_row_col))
        for widget in widgets["Controls"]:
            name1 = widget["name"]
            class1 = widget["class"]
            exec(
                f'self.{name1} = {lua_pyqt_conversion.get(class1, "QLabel")}(self.centralwidget)'
            )
            Y1 = widget["y"]
            X1 = widget["x"]
            H1 = widget["height"]
            W1 = widget["width"]
            exec(f"self.widgets_layout.addWidget(self.{name1}, {Y1}, {X1}, {H1}, {W1})")
            for i1 in range(H1):
                for i2 in range(W1):
                    widgets_map[Y1 + i1][X1 + i2] += 1
            exec(f'self.{name1}.setObjectName("{name1}")')
            if class1 == "color":
                _locals = locals()
                exec(
                    f'self.{name1}.clicked.connect(lambda: self.set_color("{name1}"))',
                    _locals,
                )
            if class1 == "coloralpha":
                _locals = locals()
                exec(
                    f'self.{name1}.clicked.connect(lambda: self.set_coloralpha("{name1}"))',
                    _locals,
                )
            if class1 == "Pyegi_button":
                _locals = locals()
                exec(
                    f"self.{name1}.clicked.connect(lambda: self.button_clicked({widget}, LuaConverter, script_settings, window_index))",
                    _locals,
                )
        all_zeros = np.zeros((max_row_col, max_row_col))
        r_trim = 0
        continue1 = True
        while continue1:
            if np.array_equal(widgets_map[r_trim:, :], all_zeros[r_trim:, :]):
                continue1 = False
            else:
                r_trim += 1
        c_trim = 0
        continue1 = True
        while continue1:
            if np.array_equal(widgets_map[:, c_trim:], all_zeros[:, c_trim:]):
                continue1 = False
            else:
                c_trim += 1
        widgets_map = widgets_map[:r_trim, :c_trim]
        empty_rows = np.where(np.sum(widgets_map, axis=1) == 0)[0]
        spacer_counter = 0
        for row_i in empty_rows:
            spacer_counter += 1
            name1 = f"spacerItem{spacer_counter}"
            exec(f"self.{name1} = QSpacerItem(10, 20)")
            exec(f"self.widgets_layout.addItem(self.{name1}, {row_i}, 0)")
            widgets_map[row_i, 0] = 1
        empty_cols = np.where(np.sum(widgets_map, axis=0) == 0)[0]
        for col_i in empty_cols:
            spacer_counter += 1
            name1 = f"spacerItem{spacer_counter}"
            exec(f"self.{name1} = QSpacerItem(20, 10)")
            exec(f"self.widgets_layout.addItem(self.{name1}, 0, {col_i})")
            widgets_map[col_i, 0] = 1

        self.window_layout.addLayout(self.widgets_layout, 0, 0)

        LuaConverter.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LuaConverter)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 813, 26))
        self.menubar.setObjectName("menubar")
        LuaConverter.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(LuaConverter)
        self.statusbar.setObjectName("statusbar")
        LuaConverter.setStatusBar(self.statusbar)

        self.retranslateUi(LuaConverter, widgets)
        QtCore.QMetaObject.connectSlotsByName(LuaConverter)

    def retranslateUi(self, LuaConverter, widgets):
        _translate = QCoreApplication.translate
        LuaConverter.setWindowTitle(_translate("LuaConverter", self.script.name))

        for widget in widgets["Controls"]:
            class1 = widget["class"]
            if class1 == "label":
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["label"]}"))'
                )
            else:
                text2 = "hint"
                exec(
                    f'self.{widget["name"]}.setToolTip(_translate("LuaConverter", {f"{widget[text2]}".encode(encoding="UTF-8")}))'
                )
            if class1 == "edit" or class1 == "Pyegi_button":
                exec(
                    f'self.{widget["name"]}.setText("{widget["text"]}")'
                )
            if class1 == "floatedit" or class1 == "intedit":
                exec2(self, f'self.{widget["name"]}.setMinimum({widget["min"]})')
                exec2(self, f'self.{widget["name"]}.setMaximum({widget["max"]})')
                if class1 == "floatedit":
                    exec2(
                        self, f'self.{widget["name"]}.setSingleStep({widget["step"]})'
                    )
                exec2(
                    self,
                    f'self.{widget["name"]}.setProperty("value", {widget["value"]})',
                )
            if class1 == "textbox":
                text2 = "text"
                exec(
                    f'self.{widget["name"]}.setPlainText(_translate("LuaConverter", {f"{widget[text2]}".encode(encoding="UTF-8")}))'
                )
                # exec(f'self.{widget["name"]}.setFixedHeight({80*widget["height"]})')
            if class1 == "dropdown":
                exec2(self, f'self.{widget["name"]}.addItems({widget["items"]})')
                exec(
                    f'self.{widget["name"]}.setCurrentText(_translate("LuaConverter", "{widget["value"]}"))'
                )
            if class1 == "checkbox":
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["label"]}"))'
                )
                exec(f'self.{widget["name"]}.setChecked({widget["value"]})')
            if class1 == "color":
                exec(
                    f'self.{widget["name"]}.setStyleSheet("background-color: {widget["value"]}")'
                )
            if class1 == "coloralpha":
                exec(
                    f'self.{widget["name"]}.setStyleSheet("background-color: rgba{tuple(i//7*255 - (-1)**(i//7+1)*int(widget["value"][i:i+2], 16) for i in (1, 3, 5, 7))}")'
                )
            if class1 == "alpha":
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["value"]}"))'
                )
                exec(f'self.{widget["name"]}.setInputMask("\#HH")')

    def button_clicked(self, button, LuaConverter, script_settings, window_index):
        widgets = script_settings["Windows"][window_index]
        if button["action"].lower() == "cancel":
            LuaConverter.close()
        else:
            for widget in widgets["Controls"]:
                name1 = widget["name"]
                class1 = widget["class"]
                if class1 == "edit":
                    exec(f"widget['text'] = self.{name1}.text()")
                if class1 == "intedit":
                    exec(f"widget['value'] = int(self.{name1}.text())")
                if class1 == "floatedit":
                    exec(f"widget['value'] = float(self.{name1}.text())")
                if class1 == "textbox":
                    exec(f"widget['text'] = self.{name1}.toPlainText()")
                if class1 == "dropdown":
                    exec(f"widget['value'] = self.{name1}.currentText()")
                if class1 == "checkbox":
                    exec(f"widget['value'] = str(self.{name1}.isChecked())")
                if class1 == "color":
                    exec(f"color_temp = self.{name1}.palette().button().color().name()")
                    exec("color_temp = color_temp.upper()")
                    exec(f"widget['value'] = color_temp")
                if class1 == "coloralpha":
                    color = eval(f"self.{name1}.palette().button().color()")
                    alpha = f"{(255 - color.alpha()):x}"
                    coloralpha_temp = f"{color.name()}" + alpha.zfill(2)
                    coloralpha_temp = coloralpha_temp.upper()
                    widget["value"] = coloralpha_temp
                if class1 == "alpha":
                    exec(f"widget['value'] = self.{name1}.text()")
                if name1[:2] == "G_":
                    all_windows = script_settings["Windows"]
                    for index2, widgets2 in enumerate(all_windows):
                        if index2 != window_index:
                            for widget2 in widgets2["Controls"]:
                                name2 = widget2["name"]
                                class2 = widget2["class"]
                                if name2 == name1:
                                    if class2 == "edit":
                                        exec(f"widget2['text'] = self.{name1}.text()")
                                    if class2 == "intedit":
                                        exec(
                                            f"widget2['value'] = int(self.{name1}.text())"
                                        )
                                    if class2 == "floatedit":
                                        exec(
                                            f"widget2['value'] = float(self.{name1}.text())"
                                        )
                                    if class2 == "textbox":
                                        exec(
                                            f"widget2['text'] = self.{name1}.toPlainText()"
                                        )
                                    if class2 == "dropdown":
                                        exec(
                                            f"widget2['value'] = self.{name1}.currentText()"
                                        )
                                    if class2 == "checkbox":
                                        exec(
                                            f"widget2['value'] = str(self.{name1}.isChecked())"
                                        )
                                    if class2 == "color":
                                        exec(
                                            f"color_temp = self.{name1}.palette().button().color().name()"
                                        )
                                        exec("color_temp = color_temp.upper()")
                                        exec(f"widget2['value'] = color_temp")
                                    if class2 == "coloralpha":
                                        color = eval(
                                            f"self.{name1}.palette().button().color()"
                                        )
                                        alpha = f"{(255 - color.alpha()):x}"
                                        coloralpha_temp = (
                                            f"{color.name()}" + alpha.zfill(2)
                                        )
                                        coloralpha_temp = coloralpha_temp.upper()
                                        widget2["value"] = coloralpha_temp
                                    if class2 == "alpha":
                                        exec(f"widget2['value'] = self.{name1}.text()")

            py_parameters_file_path = system_inputs[3]
            write_json(script_settings, py_parameters_file_path)

            if button["action"].lower() == "apply":
                self.script.run(system_inputs[1:])
                sys.exit()
            else:
                self.setupUi(LuaConverter, self.script.id, button["transition to"])

    def set_color(self, name1):
        color0 = eval(f"self.{name1}.palette().button().color()")
        color = QColorDialog.getColor(initial=color0)
        if color.isValid():
            exec(f'self.{name1}.setStyleSheet("background-color: {color.name()}")')

    def set_coloralpha(self, name1):
        color0 = eval(f"self.{name1}.palette().button().color()")
        color0.setAlpha(255 - color0.alpha())
        color = QColorDialog.getColor(
            initial=color0,
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            exec(
                f'self.{name1}.setStyleSheet("background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {255 - color.alpha()})")'
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    LuaConverter = QtWidgets.QMainWindow()
    ui = Ui_LuaConverter()
    ui.setupUi(LuaConverter)
    LuaConverter.show()
    sys.exit(app.exec())
