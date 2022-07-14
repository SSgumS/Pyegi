from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QCoreApplication
import os
import json
import qdarktheme

settings_file_path = os.path.dirname(__file__) + "/settings.json"


class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow, MainWindow):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(308, 151)
        f = open(settings_file_path)
        self.overall_settings = json.load(f)
        f.close()
        if self.overall_settings["Theme"] == "Dark":
            SettingsWindow.setStyleSheet(qdarktheme.load_stylesheet())
        elif self.overall_settings["Theme"] == "Pyegi":
            SettingsWindow.setStyleSheet(self.overall_settings["Pyegi_specs"])
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
        self.themes_combobox.addItems(["Default", "Dark", "Pyegi"])
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
        elif self.themes_combobox.currentText() == "Pyegi":
            SettingsWindow.setStyleSheet(self.overall_settings["Pyegi_specs"])
        else:
            SettingsWindow.setStyleSheet("")

    def writeSettings(self, SettingsWindow, MainWindow):
        self.overall_settings["Theme"] = self.themes_combobox.currentText()
        dummy_var = """
        * {
            color: white;
            border: none;
            padding: 3px;
        }
        QMainWindow {
            background-color: rgb(30,37,47);
        }
        QPushButton {
            background-color: rgb(41,55,66);
        }
        QPushButton:hover {
            background-color: rgb(46,205,112);
        }
        QPushButton:pressed {
            background-color: rgb(125,225,168);
            border-style: inset;
            border-width: 1px;
        }
        QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox {
            color: rgb(100,162,131);
            background-color: rgb(24,28,31);
        }
        QComboBox {
            color: rgb(100,162,131);
            background-color: rgb(24,28,31);
        }
        QComboBox QAbstractItemView {
            color: white;
            background-color: rgb(98,120,144);
        }
        QScrollBar {
            background: rgb(53,62,68);
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: rgb(53,62,68);
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background: rgb(53,62,68);
        }
        QScrollBar::handle {
            background: rgb(98,120,144);
        }
        QScrollBar::up-arrow, QScrollBar::down-arrow {
            width: 10px;
            height: 10px;
        }
        """
        json.dump(self.overall_settings, open(settings_file_path, "w"))
        if self.overall_settings["Theme"] == "Dark":
            MainWindow.setStyleSheet(qdarktheme.load_stylesheet())
        elif self.overall_settings["Theme"] == "Pyegi":
            MainWindow.setStyleSheet(self.overall_settings["Pyegi_specs"])
        else:
            MainWindow.setStyleSheet("")
        SettingsWindow.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    SettingsWindow = QtWidgets.QMainWindow()
    ui = Ui_SettingsWindow()
    ui.setupUi(SettingsWindow)
    SettingsWindow.show()
    sys.exit(app.exec())
