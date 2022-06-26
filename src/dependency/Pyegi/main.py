from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QMovie
import os
import json
import sys
from auxiliary_lua import Ui_LuaConverter

dependency_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
scriptPath = dependency_dir + 'PythonScripts/'
system_inputs = sys.argv


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 81, 16))
        self.label.setObjectName("label")
        self.scriptNames_comboBox = QtWidgets.QComboBox(
            self.centralwidget, currentIndexChanged=lambda: self.preview())
        self.scriptNames_comboBox.setGeometry(QtCore.QRect(120, 20, 651, 22))
        self.scriptNames_comboBox.setObjectName("scriptNames_comboBox")
        self.preview_label = QtWidgets.QLabel(self.centralwidget)
        self.preview_label.setGeometry(QtCore.QRect(20, 60, 761, 431))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.preview_label.setFont(font)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setObjectName("preview_label")
        self.cancel_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_pushButton.setGeometry(QtCore.QRect(20, 510, 121, 31))
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.cancel_pushButton.clicked.connect(
            QtCore.QCoreApplication.instance().quit)
        self.settings_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.settings_pushButton.setGeometry(QtCore.QRect(340, 510, 121, 31))
        self.settings_pushButton.setObjectName("settings_pushButton")
        self.next_pushButton = QtWidgets.QPushButton(
            self.centralwidget, clicked=lambda: self.openWindow(self.scriptNames_comboBox.currentText()))
        self.next_pushButton.setGeometry(QtCore.QRect(650, 510, 121, 31))
        self.next_pushButton.setObjectName("next_pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        first_item = True
        main_gif_path = ''
        for file in os.listdir(scriptPath):
            if os.path.isdir(scriptPath+file):
                self.scriptNames_comboBox.addItem(file)
                if first_item:
                    first_item = False
                    for file2 in os.listdir(scriptPath+file):
                        if file2.endswith(".gif"):
                            main_gif_path = scriptPath+file+'/'+file2

        if main_gif_path != '':
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Select Script"))
        self.preview_label.setText(_translate("MainWindow", "Preview"))
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.settings_pushButton.setText(_translate("MainWindow", "Settings"))
        self.next_pushButton.setText(_translate("MainWindow", "Next"))

    def openWindow(self, script_name):
        script_settings = scriptPath + f'{script_name}/settings.json'
        f = open(script_settings)
        widgets = json.load(f)
        f.close()
        if widgets['Format'].lower() == "lua":
            self.window = QtWidgets.QMainWindow()
            self.ui = Ui_LuaConverter()
            self.ui.setupUi(self.window, script_name)
            self.window.show()
        else:
            os.system(
                f'""{dependency_dir}.venv/Scripts/python.exe" "{scriptPath}{script_name}/main.py" "{system_inputs[1]}" "{system_inputs[2]}""')

    def preview(self):
        main_gif_path = ''
        scriptFolder = self.scriptNames_comboBox.currentText()
        for file in os.listdir(scriptPath+scriptFolder):
            if file.endswith(".gif"):
                main_gif_path = scriptPath+scriptFolder+'/'+file
        if main_gif_path != '':
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(False)
            # self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            # print(self.movie.CacheMode(0))
            # self.movie.loopCount()
        else:
            self.preview_label.setText('No Preview')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
