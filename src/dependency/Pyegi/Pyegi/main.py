from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
import os
import json
import sys

dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
system_inputs = sys.argv


class ComboBoxLineEdit(QtWidgets.QLineEdit):
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(e)

        combobox: QtWidgets.QComboBox = self.parent()
        completer = combobox.completer()

        if combobox.currentText() == "":
            completer.setCompletionMode(
                QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion
            )
        else:
            completer.setCompletionMode(
                QtWidgets.QCompleter.CompletionMode.PopupCompletion
            )
        completer.complete()

    def keyPressEvent(self, e: QtGui.QMouseEvent) -> None:
        super().keyPressEvent(e)

        combobox: QtWidgets.QComboBox = self.parent()
        completer = combobox.completer()

        if combobox.currentText() == "":
            completer.setCompletionMode(
                QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion
            )
        else:
            completer.setCompletionMode(
                QtWidgets.QCompleter.CompletionMode.PopupCompletion
            )
        completer.complete()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ScriptSelection_label = QtWidgets.QLabel(self.centralwidget)
        self.ScriptSelection_label.setGeometry(QtCore.QRect(30, 20, 81, 16))
        self.ScriptSelection_label.setObjectName("ScriptSelection_label")

        # combobox
        self.selected_script = ""
        self.combobox = QtWidgets.QComboBox(self.centralwidget)
        self.combobox.setGeometry(QtCore.QRect(120, 20, 651, 22))
        self.combobox.setObjectName("scriptNames_comboBox")
        combobox_items = []
        for script_name in os.listdir(scriptsPath):
            if not os.path.isdir(scriptsPath + script_name):
                continue
            self.combobox.addItem(script_name)
            combobox_items.append(script_name)
        self.combobox.setLineEdit(ComboBoxLineEdit(self.combobox))
        self.combobox.lineEdit().setPlaceholderText("Please select a script.")
        self.combobox.setCurrentIndex(-1)
        completer = QtWidgets.QCompleter(combobox_items)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.combobox.setCompleter(completer)
        self.combobox.currentIndexChanged.connect(self.preview)
        self.combobox.currentTextChanged.connect(self.textChangedHandler)

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
        self.cancel_pushButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.settings_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.settings_pushButton.setGeometry(QtCore.QRect(150, 510, 121, 31))
        self.settings_pushButton.setObjectName("settings_pushButton")
        self.next_pushButton = QtWidgets.QPushButton(
            self.centralwidget, clicked=self.writeMainWindowOutput
        )
        self.next_pushButton.setGeometry(QtCore.QRect(650, 510, 121, 31))
        self.next_pushButton.setObjectName("next_pushButton")
        self.LinesSelection_label = QtWidgets.QLabel(self.centralwidget)
        self.LinesSelection_label.setGeometry(QtCore.QRect(430, 510, 85, 16))
        self.LinesSelection_label.setObjectName("LinesSelection_label")
        self.SelectedLines_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.SelectedLines_radioButton.setGeometry(QtCore.QRect(520, 510, 100, 20))
        self.SelectedLines_radioButton.setChecked(True)
        self.SelectedLines_radioButton.setObjectName("SelectedLines_radioButton")
        self.AllLines_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.AllLines_radioButton.setGeometry(QtCore.QRect(520, 530, 100, 20))
        self.AllLines_radioButton.setObjectName("AllLines_radioButton")
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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
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
        QtCore.QCoreApplication.instance().quit()

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
                    QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion
                )
                completer.setCompletionPrefix(text)  # QCompleter is not updated yet...
                completer.complete()  # TODO: doesn't work :/!
        else:
            completer.setCompletionMode(
                QtWidgets.QCompleter.CompletionMode.PopupCompletion
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
