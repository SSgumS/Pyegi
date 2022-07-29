from PyQt6 import QtCore, QtGui, QtWidgets
import os
import json
import sys
from auxiliary_lua import Ui_LuaConverter
from os.path import exists

dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
system_inputs = sys.argv


class Ui_EmptyWindow(object):
    def setupUi(self, EmptyWindow):
        EmptyWindow.setObjectName("EmptyWindow")
        EmptyWindow.resize(825, 600)
        self.centralwidget = QtWidgets.QWidget(EmptyWindow)
        self.centralwidget.setObjectName("centralwidget")
        EmptyWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(EmptyWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 825, 26))
        self.menubar.setObjectName("menubar")
        EmptyWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(EmptyWindow)
        self.statusbar.setObjectName("statusbar")
        EmptyWindow.setStatusBar(self.statusbar)

        script_name = system_inputs[4]
        script_settings = scriptsPath + f"{script_name}/settings.json"
        f = open(script_settings)
        widgets = json.load(f)
        f.close()

        if widgets["Format"].lower() == "lua":
            self.window = QtWidgets.QMainWindow()
            self.ui = Ui_LuaConverter()
            self.ui.setupUi(self.window, script_name)
            self.window.show()
        else:
            arguments = '"' + '" "'.join(system_inputs[1:]) + '"'
            if exists(f"{scriptsPath}{script_name}/.venv/Scripts/python.exe"):
                os.system(
                    f'""{scriptsPath}{script_name}/.venv/Scripts/python.exe" "{scriptsPath}{script_name}/main.py" {arguments}"'
                )
            else:
                print(
                    "There's something wrong with the script environment. Switching to Pyegi environment..."
                )
                os.system(
                    f'""{dependency_dir}.venv/Scripts/python.exe" "{scriptsPath}{script_name}/main.py" {arguments}"'
                )
            sys.exit()

        self.retranslateUi(EmptyWindow)
        QtCore.QMetaObject.connectSlotsByName(EmptyWindow)

    def retranslateUi(self, EmptyWindow):
        _translate = QtCore.QCoreApplication.translate
        EmptyWindow.setWindowTitle(_translate("EmptyWindow", "MainWindow"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    EmptyWindow = QtWidgets.QMainWindow()
    ui = Ui_EmptyWindow()
    ui.setupUi(EmptyWindow)
    EmptyWindow.hide()
    sys.exit(app.exec())
