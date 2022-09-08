from PyQt6 import QtCore, QtGui, QtWidgets
import os
import json
import sys
from auxiliary_lua import Ui_LuaConverter
from utils import (
    GLOBAL_PATHS,
    FeedFile,
)


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

        script_id = system_inputs[4]
        self.script = FeedFile().get_script(script_id)

        with open(self.script.folder + GLOBAL_PATHS.settings_filename) as file:
            widgets = json.load(file)
        if widgets["Format"].lower() == "lua":
            self.window = QtWidgets.QMainWindow()
            self.ui = Ui_LuaConverter()
            self.ui.setupUi(self.window, script_id)
            self.window.show()
        else:
            self.script.run(system_inputs[1:])
            sys.exit()

        self.retranslateUi(EmptyWindow)
        QtCore.QMetaObject.connectSlotsByName(EmptyWindow)

    def retranslateUi(self, EmptyWindow):
        _translate = QtCore.QCoreApplication.translate
        EmptyWindow.setWindowTitle(_translate("EmptyWindow", "Empty Window"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    EmptyWindow = QtWidgets.QMainWindow()
    ui = Ui_EmptyWindow()
    ui.setupUi(EmptyWindow)
    EmptyWindow.hide()
    sys.exit(app.exec())
