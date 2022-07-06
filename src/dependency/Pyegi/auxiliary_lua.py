from PyQt6 import QtCore, QtGui, QtWidgets
import os
from os.path import exists
import json
import sys


dependency_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
system_inputs = sys.argv


def exec2(self, string):
    try:
        return exec(string)
    except:
        pass


class Ui_LuaConverter(object):
    def setupUi(self, LuaConverter, script_name, window_name="main_window"):
        LuaConverter.setObjectName("LuaConverter")

        self.centralwidget = QtWidgets.QWidget(LuaConverter)
        self.centralwidget.setObjectName("centralwidget")

        if exists(system_inputs[3]):
            script_settings_file_path = system_inputs[3]
        else:
            script_settings_file_path = scriptsPath + f"{script_name}/settings.json"

        f = open(script_settings_file_path)
        script_settings = json.load(f)
        f.close()

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
        for widget in widgets["Controls"]:
            name1 = widget["name"]
            class1 = widget["class"]
            exec(
                f'self.{name1} = QtWidgets.{lua_pyqt_conversion.get(class1, "QLabel")}(self.centralwidget)'
            )
            Xtemp = offX + defW * widget["x"]
            Ytemp = offY + defH * widget["y"]
            Wtemp = defW * widget["width"]
            Htemp = defH * widget["height"]
            if Xtemp + Wtemp > Wfinal:
                Wfinal = Xtemp + Wtemp
            if Ytemp + Htemp > Hfinal:
                Hfinal = Ytemp + Htemp
            exec(
                f"self.{name1}.setGeometry(QtCore.QRect({Xtemp}, {Ytemp}, {Wtemp}, {Htemp}))"
            )
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
                    f"self.{name1}.clicked.connect(lambda: self.button_clicked({widget}, LuaConverter, script_settings, script_name, window_index))",
                    _locals,
                )
        Wfinal += offX
        Hfinal += offY
        Wfinal = max(Wfinal, 200)
        LuaConverter.resize(Wfinal, Hfinal)

        LuaConverter.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LuaConverter)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 813, 26))
        self.menubar.setObjectName("menubar")
        LuaConverter.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(LuaConverter)
        self.statusbar.setObjectName("statusbar")
        LuaConverter.setStatusBar(self.statusbar)

        self.retranslateUi(LuaConverter, widgets, script_name)
        QtCore.QMetaObject.connectSlotsByName(LuaConverter)

    def retranslateUi(self, LuaConverter, widgets, script_name):
        _translate = QtCore.QCoreApplication.translate
        LuaConverter.setWindowTitle(_translate("LuaConverter", script_name))

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
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["text"]}"))'
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

    def button_clicked(
        self, button, LuaConverter, script_settings, script_name, window_index
    ):
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
                    exec(
                        f"widget['value'] = self.{name1}.palette().button().color().name()"
                    )
                if class1 == "coloralpha":
                    color = eval(f"self.{name1}.palette().button().color()")
                    alpha = f"{(255 - color.alpha()):x}"
                    widget["value"] = f"{color.name()}" + alpha.zfill(2)
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
                                            f"widget2['value'] = self.{name1}.palette().button().color().name()"
                                        )
                                    if class2 == "coloralpha":
                                        color = eval(
                                            f"self.{name1}.palette().button().color()"
                                        )
                                        alpha = f"{(255 - color.alpha()):x}"
                                        widget2[
                                            "value"
                                        ] = f"{color.name()}" + alpha.zfill(2)
                                    if class2 == "alpha":
                                        exec(f"widget2['value'] = self.{name1}.text()")

            py_parameters_file_path = system_inputs[3]
            with open(py_parameters_file_path, "w") as outfile:
                json.dump(script_settings, outfile)

            if button["action"].lower() == "apply":
                os.system(
                    f'""{dependency_dir}.venv/Scripts/python.exe" "{scriptsPath}{script_name}/main.py" "{system_inputs[1]}" "{system_inputs[2]}" "{py_parameters_file_path}" "{system_inputs[4]}" "{system_inputs[5]}""'
                )
                sys.exit()
            else:
                self.setupUi(LuaConverter, script_name, button["transition to"])

    def set_color(self, name1):
        color0 = eval(f"self.{name1}.palette().button().color()")
        color = QtWidgets.QColorDialog.getColor(initial=color0)
        if color.isValid():
            exec(f'self.{name1}.setStyleSheet("background-color: {color.name()}")')

    def set_coloralpha(self, name1):
        color0 = eval(f"self.{name1}.palette().button().color()")
        color0.setAlpha(255 - color0.alpha())
        color = QtWidgets.QColorDialog.getColor(
            initial=color0,
            options=QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel,
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
