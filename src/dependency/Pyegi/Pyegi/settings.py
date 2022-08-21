from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QCoreApplication
import os
import json
from utils import set_style, Theme, get_settings

utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


class Ui_SettingsWindow:
    def setupUi(self, SettingsWindow, main_ui=None):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(308, 171)
        self.overall_settings = get_settings()
        set_style(SettingsWindow, self.overall_settings["Theme"])
        self.centralwidget = QtWidgets.QWidget(SettingsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QtWidgets.QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.theme_label = QtWidgets.QLabel(self.centralwidget)
        self.theme_label.setObjectName("theme_label")
        self.widgets_layout.addWidget(self.theme_label, 0, 0, 1, 1)
        self.themes_combobox = QtWidgets.QComboBox(self.centralwidget)
        self.themes_combobox.setObjectName("themes_combobox")
        combobox_items = [Theme.SYSTEM.value, Theme.DARK.value, Theme.LIGHT.value]
        for f in os.listdir(themes_path):
            whole_name = f.split(".")
            filename = whole_name[0].split("/")[-1]
            combobox_items.append(filename)
        self.themes_combobox.addItems(combobox_items)
        self.widgets_layout.addWidget(self.themes_combobox, 0, 1, 1, 5)
        self.themes_combobox.setCurrentText(self.overall_settings["Theme"])
        self.themes_combobox.currentTextChanged.connect(
            lambda: set_style(SettingsWindow, self.themes_combobox.currentText())
        )

        self.feeds_label = QtWidgets.QLabel(self.centralwidget)
        self.feeds_label.setObjectName("feeds_label")
        self.widgets_layout.addWidget(self.feeds_label, 1, 0, 1, 5)
        self.feeds_spinbox = QtWidgets.QSpinBox(self.centralwidget)
        self.feeds_spinbox.setObjectName("feeds_spinbox")
        self.widgets_layout.addWidget(self.feeds_spinbox, 1, 5, 1, 1)
        self.feeds_spinbox.setMinimum(1)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.widgets_layout.addItem(spacerItem, 2, 0, 1, 1)
        self.cancel_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.widgets_layout.addWidget(self.cancel_pushButton, 3, 0, 1, 1)
        self.cancel_pushButton.clicked.connect(lambda: SettingsWindow.close())
        self.ok_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ok_pushButton.setObjectName("ok_pushButton")
        self.widgets_layout.addWidget(self.ok_pushButton, 3, 5, 1, 1)
        self.ok_pushButton.clicked.connect(
            lambda: self.writeSettings(SettingsWindow, main_ui)
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
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "Settings"))
        self.theme_label.setText(_translate("SettingsWindow", "Theme"))
        self.feeds_label.setText(
            _translate(
                "SettingsWindow",
                "Update feed interval (Days):",
            )
        )
        self.feeds_spinbox.setValue(self.overall_settings["Automatic feeds update"])
        self.cancel_pushButton.setText(_translate("SettingsWindow", "Cancel"))
        self.ok_pushButton.setText(_translate("SettingsWindow", "OK"))

    def writeSettings(self, SettingsWindow, main_ui):
        self.overall_settings["Theme"] = self.themes_combobox.currentText()
        self.overall_settings["Automatic feeds update"] = int(self.feeds_spinbox.text())
        json.dump(self.overall_settings, open(settings_file_path, "w"), indent=4)
        if main_ui:
            set_style(main_ui.window, self.overall_settings["Theme"])
        SettingsWindow.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    SettingsWindow = QtWidgets.QMainWindow()
    ui = Ui_SettingsWindow()
    ui.setupUi(SettingsWindow)
    SettingsWindow.show()
    sys.exit(app.exec())
