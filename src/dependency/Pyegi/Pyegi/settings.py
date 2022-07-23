from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication
import os
import json
import qdarktheme

utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow, MainWindow):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(308, 151)
        f = open(settings_file_path)
        self.overall_settings = json.load(f)
        f.close()
        if self.overall_settings["Theme"] == "Dark":
            SettingsWindow.setStyleSheet(qdarktheme.load_stylesheet())
        elif self.overall_settings["Theme"] == "Light":
            SettingsWindow.setStyleSheet(qdarktheme.load_stylesheet("light"))
        elif self.overall_settings["Theme"] == "Default":
            SettingsWindow.setStyleSheet("")
        else:
            f = open(f"{themes_path}{self.overall_settings['Theme']}.css", "r")
            theme_data = f.read()
            f.close()
            SettingsWindow.setStyleSheet(theme_data)
        self.centralwidget = QtWidgets.QWidget(SettingsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QtWidgets.QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.theme_label = QtWidgets.QLabel(self.centralwidget)
        self.theme_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.theme_label.setObjectName("theme_label")
        self.widgets_layout.addWidget(self.theme_label, 0, 0, 1, 1)
        self.themes_combobox = QtWidgets.QComboBox(self.centralwidget)
        self.themes_combobox.setObjectName("themes_combobox")
        combobox_items = ["Default", "Dark", "Light"]
        for f in os.listdir(themes_path):
            whole_name = f.split(".")
            filename = whole_name[0].split("/")[-1]
            combobox_items.append(filename)
        self.themes_combobox.addItems(combobox_items)
        self.widgets_layout.addWidget(self.themes_combobox, 0, 1, 1, 1)
        self.themes_combobox.setCurrentText(self.overall_settings["Theme"])
        self.themes_combobox.currentTextChanged.connect(
            lambda: self.applyTheme(SettingsWindow)
        )
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.widgets_layout.addItem(spacerItem, 1, 0, 1, 1)
        self.cancel_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.widgets_layout.addWidget(self.cancel_pushButton, 2, 0, 1, 1)
        self.cancel_pushButton.clicked.connect(lambda: SettingsWindow.close())
        self.ok_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ok_pushButton.setObjectName("ok_pushButton")
        self.widgets_layout.addWidget(self.ok_pushButton, 2, 1, 1, 1)
        self.ok_pushButton.clicked.connect(
            lambda: self.writeSettings(SettingsWindow, MainWindow)
        )
        self.window_layout.addLayout(self.widgets_layout, 0, 0, 1, 1)
        SettingsWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SettingsWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 308, 26))
        self.menubar.setObjectName("menubar")
        SettingsWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(SettingsWindow)
        self.statusbar.setObjectName("statusbar")
        SettingsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(SettingsWindow)
        QtCore.QMetaObject.connectSlotsByName(SettingsWindow)

    def retranslateUi(self, SettingsWindow):
        _translate = QtCore.QCoreApplication.translate
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "MainWindow"))
        self.theme_label.setText(_translate("SettingsWindow", "Theme"))
        self.cancel_pushButton.setText(_translate("SettingsWindow", "Cancel"))
        self.ok_pushButton.setText(_translate("SettingsWindow", "OK"))

    def applyTheme(self, SettingsWindow):
        if self.themes_combobox.currentText() == "Dark":
            SettingsWindow.setStyleSheet(qdarktheme.load_stylesheet())
        elif self.themes_combobox.currentText() == "Light":
            SettingsWindow.setStyleSheet(qdarktheme.load_stylesheet("light"))
        elif self.themes_combobox.currentText() == "Default":
            SettingsWindow.setStyleSheet("")
        else:
            f = open(f"{themes_path}{self.themes_combobox.currentText()}.css", "r")
            theme_data = f.read()
            f.close()
            SettingsWindow.setStyleSheet(theme_data)

    def writeSettings(self, SettingsWindow, MainWindow):
        self.overall_settings["Theme"] = self.themes_combobox.currentText()
        json.dump(self.overall_settings, open(settings_file_path, "w"))
        if self.overall_settings["Theme"] == "Dark":
            MainWindow.setStyleSheet(qdarktheme.load_stylesheet())
        elif self.overall_settings["Theme"] == "Light":
            MainWindow.setStyleSheet(qdarktheme.load_stylesheet("light"))
        elif self.overall_settings["Theme"] == "Default":
            MainWindow.setStyleSheet("")
        else:
            f = open(f"{themes_path}{self.overall_settings['Theme']}.css", "r")
            theme_data = f.read()
            f.close()
            MainWindow.setStyleSheet(theme_data)
        SettingsWindow.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    SettingsWindow = QtWidgets.QMainWindow()
    ui = Ui_SettingsWindow()
    ui.setupUi(SettingsWindow)
    SettingsWindow.show()
    sys.exit(app.exec())
