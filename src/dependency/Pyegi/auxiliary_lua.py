from PyQt6 import QtCore, QtGui, QtWidgets
import os
import json
import sys

dependency_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
scriptPath = dependency_dir + 'PythonScripts/'
system_inputs = sys.argv


def exec2(self, string):
    try:
        return exec(string)
    except:
        pass


class Ui_LuaConverter(object):
    def setupUi(self, LuaConverter, script_name):
        LuaConverter.setObjectName("LuaConverter")

        self.centralwidget = QtWidgets.QWidget(LuaConverter)
        self.centralwidget.setObjectName("centralwidget")

        script_settings = scriptPath + f'{script_name}/settings.json'
        f = open(script_settings)
        widgets = json.load(f)
        f.close()

        defW = 120  # default width
        defH = 25  # default height
        offX = 20  # offset in the X axis direction
        offY = 25  # offset in the Y axis direction
        Wfinal = 0  # final width of the window
        Hfinal = 0  # final height of the window
        lua_pyqt_conversion = {
            'label': 'QLabel',
            'edit': 'QLineEdit',
            'intedit': 'QSpinBox',
            'floatedit': 'QDoubleSpinBox',
            'textbox': 'QTextEdit',
            'dropdown': 'QComboBox',
            'checkbox': 'QCheckBox',
            'color': 'QPushButton',
            'coloralpha': 'QPushButton',
            'alpha': 'QLineEdit'
        }
        for widget in widgets['Controls']:
            name1 = widget['name']
            class1 = widget['class']
            exec(
                f'self.{name1} = QtWidgets.{lua_pyqt_conversion.get(class1, "QLabel")}(self.centralwidget)')
            Xtemp = offX + defW*widget["x"]
            Ytemp = offY + defH*widget["y"]
            Wtemp = defW*widget["width"]
            Htemp = defH*widget["height"]
            if Xtemp + Wtemp > Wfinal:
                Wfinal = Xtemp + Wtemp
            if Ytemp + Htemp > Hfinal:
                Hfinal = Ytemp + Htemp
            exec(
                f'self.{name1}.setGeometry(QtCore.QRect({Xtemp}, {Ytemp}, {Wtemp}, {Htemp}))')
            exec(f'self.{name1}.setObjectName("{name1}")')
            if class1 == 'color':
                _locals = locals()
                exec(
                    f'self.{name1}.clicked.connect(lambda: self.set_color("{name1}"))', _locals)
            if class1 == 'coloralpha':
                _locals = locals()
                exec(
                    f'self.{name1}.clicked.connect(lambda: self.set_coloralpha("{name1}"))', _locals)
        Wfinal += offX
        Hfinal += offY + 70
        LuaConverter.resize(Wfinal, Hfinal)

        self.cancel_pushButton = QtWidgets.QPushButton(
            self.centralwidget, clicked=lambda: self.closeSecond(LuaConverter))
        self.cancel_pushButton.setGeometry(
            QtCore.QRect(offX, Hfinal-offY-30, 80, 30))
        self.cancel_pushButton.setObjectName("cancel_pushButton")

        self.apply_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.apply_pushButton.setGeometry(
            QtCore.QRect(Wfinal-offX-80, Hfinal-offY-30, 80, 30))
        self.apply_pushButton.setObjectName("apply_pushButton")
        self.apply_pushButton.clicked.connect(
            lambda: self.apply_inputs(widgets, script_name, dependency_dir))

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

        for widget in widgets['Controls']:
            class1 = widget['class']
            if class1 == 'label':
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["label"]}"))')
            else:
                text2 = "hint"
                exec(
                    f'self.{widget["name"]}.setToolTip(_translate("LuaConverter", {f"{widget[text2]}".encode(encoding="UTF-8")}))')
            if class1 == 'edit':
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["text"]}"))')
            if class1 == 'floatedit' or class1 == 'intedit':
                exec2(
                    self, f'self.{widget["name"]}.setMinimum({widget["min"]})')
                exec2(
                    self, f'self.{widget["name"]}.setMaximum({widget["max"]})')
                if class1 == 'floatedit':
                    exec2(
                        self, f'self.{widget["name"]}.setSingleStep({widget["step"]})')
                exec2(
                    self, f'self.{widget["name"]}.setProperty("value", {widget["value"]})')
            if class1 == 'textbox':
                text2 = "text"
                exec(
                    f'self.{widget["name"]}.setPlainText(_translate("LuaConverter", {f"{widget[text2]}".encode(encoding="UTF-8")}))')
            if class1 == 'dropdown':
                exec2(
                    self, f'self.{widget["name"]}.addItems({widget["items"]})')
                exec(
                    f'self.{widget["name"]}.setCurrentText(_translate("LuaConverter", "{widget["value"]}"))')
            if class1 == 'checkbox':
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["label"]}"))')
                exec(
                    f'self.{widget["name"]}.setChecked({widget["value"]})')
            if class1 == 'color':
                exec(
                    f'self.{widget["name"]}.setStyleSheet("background-color: {widget["value"]}")')
            if class1 == 'coloralpha':
                exec(
                    f'self.{widget["name"]}.setStyleSheet("background-color: rgba{tuple(i//7*255 - (-1)**(i//7+1)*int(widget["value"][i:i+2], 16) for i in (1, 3, 5, 7))}")')
            if class1 == 'alpha':
                exec(
                    f'self.{widget["name"]}.setText(_translate("LuaConverter", "{widget["value"]}"))')
                exec(
                    f'self.{widget["name"]}.setInputMask("\#HH")')

        self.cancel_pushButton.setText(_translate("LuaConverter", "Cancel"))
        self.apply_pushButton.setText(_translate("LuaConverter", "Apply"))

    def closeSecond(self, second_w):
        second_w.close()

    def apply_inputs(self, widgets, script_name, dependency_dir):
        for widget in widgets['Controls']:
            name1 = widget['name']
            class1 = widget['class']
            if class1 == 'edit':
                exec(f"widget['text'] = self.{name1}.text()")
            if class1 == 'intedit':
                exec(f"widget['value'] = int(self.{name1}.text())")
            if class1 == 'floatedit':
                exec(f"widget['value'] = float(self.{name1}.text())")
            if class1 == 'textbox':
                exec(f"widget['text'] = self.{name1}.toPlainText()")
            if class1 == 'dropdown':
                exec(f"widget['value'] = self.{name1}.currentText()")
            if class1 == 'checkbox':
                exec(f"widget['value'] = str(self.{name1}.isChecked())")
            if class1 == 'color':
                exec(
                    f"widget['value'] = self.{name1}.palette().button().color().name()")
            if class1 == 'coloralpha':
                color = eval(f'self.{name1}.palette().button().color()')
                alpha = f"{(255 - color.alpha()):x}"
                widget['value'] = f"{color.name()}" + alpha.zfill(2)
            if class1 == 'alpha':
                exec(f"widget['value'] = self.{name1}.text()")

        py_parameters_file_path = system_inputs[3]
        with open(py_parameters_file_path, 'w') as outfile:
            json.dump(widgets, outfile)

        os.system(
            f'""{dependency_dir}.venv/Scripts/python.exe" "{scriptPath}{script_name}/main.py" "{system_inputs[1]}" "{system_inputs[2]}" "{py_parameters_file_path}""')
        sys.exit()

    def set_color(self, name1):
        color0 = eval(f'self.{name1}.palette().button().color()')
        color = QtWidgets.QColorDialog.getColor(initial=color0)
        if color.isValid():
            exec(
                f'self.{name1}.setStyleSheet("background-color: {color.name()}")')

    def set_coloralpha(self, name1):
        color0 = eval(f'self.{name1}.palette().button().color()')
        color0.setAlpha(255 - color0.alpha())
        color = QtWidgets.QColorDialog.getColor(initial=color0,
                                                options=QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            exec(
                f'self.{name1}.setStyleSheet("background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {255 - color.alpha()})")')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LuaConverter = QtWidgets.QMainWindow()
    ui = Ui_LuaConverter()
    ui.setupUi(LuaConverter)
    LuaConverter.show()
    sys.exit(app.exec())
