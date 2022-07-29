from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QComboBox,
    QCompleter,
    QGridLayout,
    QSizePolicy,
    QLabel,
    QRadioButton,
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QMovie
import os
import json
import sys
from settings import Ui_SettingsWindow
from utils import set_style

dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
system_inputs = sys.argv
utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


class QPushButton2(QPushButton):
    def __init__(self, parent: QPushButton):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )


class ComboBoxLineEdit(QLineEdit):
    def mousePressEvent(self, e: QMouseEvent) -> None:
        super().mousePressEvent(e)

        combobox: QComboBox = self.parent()
        completer = combobox.completer()
        if combobox.currentText() == "":
            completer.setCompletionMode(
                QCompleter.CompletionMode.UnfilteredPopupCompletion
            )
        else:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setCompletionPrefix(combobox.currentText())
        completer.complete()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        super().keyPressEvent(e)

        combobox: QComboBox = self.parent()
        if combobox.currentText() != "":
            return
        completer = combobox.completer()
        completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        completer.complete()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(825, 600)
        self = set_style(self, MainWindow)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.ScriptSelection_label = QLabel(self.centralwidget)
        self.ScriptSelection_label.setObjectName("ScriptSelection_label")
        self.widgets_layout.addWidget(self.ScriptSelection_label, 0, 0, 1, 1)

        # combobox
        self.selected_script = ""
        self.combobox = QComboBox(self.centralwidget)
        self.combobox.setObjectName("scriptNames_comboBox")
        self.widgets_layout.addWidget(self.combobox, 0, 1, 1, 5)
        combobox_items = []
        for script_name in os.listdir(scriptsPath):
            if not os.path.isdir(scriptsPath + script_name):
                continue
            self.combobox.addItem(script_name)
            combobox_items.append(script_name)
        self.combobox.setLineEdit(ComboBoxLineEdit(self.combobox))
        self.combobox.lineEdit().setPlaceholderText("Please select a script.")
        self.combobox.setCurrentIndex(-1)
        completer = QCompleter(combobox_items)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combobox.setCompleter(completer)
        self.combobox.currentIndexChanged.connect(self.preview)
        self.combobox.currentTextChanged.connect(self.textChangedHandler)

        self.preview_label = QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.preview_label.setFont(font)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setObjectName("preview_label")
        self.widgets_layout.addWidget(self.preview_label, 1, 0, 7, 6)
        self.cancel_pushButton = QPushButton2(self.centralwidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.widgets_layout.addWidget(self.cancel_pushButton, 8, 0, 2, 1)
        self.cancel_pushButton.clicked.connect(QCoreApplication.instance().quit)
        self.settings_pushButton = QPushButton2(self.centralwidget)
        self.settings_pushButton.setObjectName("settings_pushButton")
        self.widgets_layout.addWidget(self.settings_pushButton, 8, 1, 2, 1)
        self.settings_pushButton.clicked.connect(
            lambda: self.openSettingsWindow(MainWindow)
        )
        self.next_pushButton = QPushButton2(self.centralwidget)
        self.next_pushButton.setObjectName("next_pushButton")
        self.widgets_layout.addWidget(self.next_pushButton, 8, 5, 2, 1)
        self.next_pushButton.clicked.connect(self.writeMainWindowOutput)
        self.LinesSelection_label = QLabel(self.centralwidget)
        self.LinesSelection_label.setObjectName("LinesSelection_label")
        self.LinesSelection_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.widgets_layout.addWidget(self.LinesSelection_label, 8, 3, 1, 1)
        self.SelectedLines_radioButton = QRadioButton(self.centralwidget)
        self.SelectedLines_radioButton.setChecked(True)
        self.SelectedLines_radioButton.setObjectName("SelectedLines_radioButton")
        self.widgets_layout.addWidget(self.SelectedLines_radioButton, 8, 4, 1, 1)
        self.AllLines_radioButton = QRadioButton(self.centralwidget)
        self.AllLines_radioButton.setObjectName("AllLines_radioButton")
        self.widgets_layout.addWidget(self.AllLines_radioButton, 9, 4, 1, 1)
        self.window_layout.addLayout(self.widgets_layout, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 825, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ScriptSelection_label.setText(_translate("MainWindow", "Select Script"))
        self.preview_label.setText(
            _translate("MainWindow", "No script selected to preview.")
        )
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.settings_pushButton.setText(_translate("MainWindow", "Settings"))
        self.next_pushButton.setText(_translate("MainWindow", "Next"))
        self.LinesSelection_label.setText(_translate("MainWindow", "Apply script on:"))
        self.SelectedLines_radioButton.setText(
            _translate("MainWindow", "selected line(s)")
        )
        self.AllLines_radioButton.setText(_translate("MainWindow", "all lines"))

    def openSettingsWindow(self, MainWindow):
        window = QtWidgets.QMainWindow()
        ui = Ui_SettingsWindow()
        ui.setupUi(window, MainWindow)
        window.show()

    def writeMainWindowOutput(self):
        if self.selected_script == "":
            return
        main_py_parameters = {}
        if self.AllLines_radioButton.isChecked():
            main_py_parameters["applyOn"] = "all lines"
        else:
            main_py_parameters["applyOn"] = "selected lines"
        main_py_parameters["selectedScript"] = self.selected_script
        json.dump(main_py_parameters, open(system_inputs[1], "w"))
        QCoreApplication.instance().quit()

    def preview(self):
        if self.combobox.currentIndex() == -1:
            self.preview_label.setText("No script selected to preview.")
            self.selected_script = ""
        else:
            self.selected_script = self.combobox.itemText(self.combobox.currentIndex())
        main_gif_path = ""
        scriptFolder = self.selected_script
        for file in os.listdir(scriptsPath + scriptFolder):
            if file.endswith(".gif"):
                main_gif_path = scriptsPath + scriptFolder + "/" + file
        if main_gif_path != "":
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(False)
            # self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            # print(self.movie.CacheMode(0))
            # self.movie.loopCount()
        else:
            self.preview_label.setText(f"No preview for {scriptFolder}.")

    def textChangedHandler(self, text: str):
        combobox = self.combobox
        completer = combobox.completer()
        if text == "":
            if combobox.hasFocus():
                completer.setCompletionMode(
                    QCompleter.CompletionMode.UnfilteredPopupCompletion
                )
                completer.setCompletionPrefix(text)  # QCompleter is not updated yet...
                # completer.complete()  # TODO: doesn't work :/!
        else:
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
