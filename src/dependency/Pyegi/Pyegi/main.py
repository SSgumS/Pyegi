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
    QTextBrowser,
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QMovie
import os
from os.path import exists
import json
import sys
import toml
import re
from settings import Ui_SettingsWindow
from scripts_handler import Ui_ScriptsHandlerWindow
from utils import set_style, try_except, get_settings, ComboBoxLineEdit
from installer import development_mode
from datetime import datetime

if development_mode:
    print(">>>>>>>>>>  Development mode  <<<<<<<<<<")

dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
system_inputs = sys.argv
utils_path = os.path.dirname(__file__)
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"


def get_description_value(poetry_data, pyegi_data, attr):
    try:
        output = pyegi_data[attr]
    except:
        output = try_except(poetry_data, attr)
    if attr == "authors":
        try:
            for i, str in enumerate(output):
                output[i] = re.sub(
                    "(.+) ?\<(.+)>", '<a href="mailto: \\2">\\1</a>', str
                )
        except:
            pass
    return output


def convert_to_header(str):
    return f"<html><b>{str}:</b></html>"


def get_description(script_name):
    pyproject_file_path = f"{scriptsPath}{script_name}/pyproject.toml"
    script_description = ""
    if exists(pyproject_file_path):
        pyproject_data = toml.load(pyproject_file_path)
        poetry_data = try_except(pyproject_data["tool"], "poetry")
        pyegi_data = try_except(pyproject_data["tool"], "pyegi")
        desired_attributes = [
            "name",
            "description",
            "version",
            "version-description",
            "authors",
        ]
        description_values = []
        for attr in desired_attributes:
            description_value = get_description_value(poetry_data, pyegi_data, attr)
            description_values.append(description_value)
        headers = [convert_to_header(str) for str in desired_attributes]
        for header, description_value in zip(headers, description_values):
            script_description += f"{header}<br>{description_value}<br><br>"
    return script_description


class QPushButton2(QPushButton):
    def __init__(self, parent: QPushButton):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )


class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.ControlElement.CE_TabBarTabLabel, opt)
            painter.restore()


class WestTabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(825, 600)
        set_style(MainWindow)
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
        self.completer = QCompleter(combobox_items)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combobox.setCompleter(self.completer)
        self.combobox.currentIndexChanged.connect(self.preview)
        self.combobox.currentTextChanged.connect(self.textChangedHandler)

        self.scriptSpecs_tabs = WestTabWidget(self.centralwidget)
        self.scriptSpecs_tabs.setObjectName("scriptSpecs_tab")
        QtWidgets.QTabBar.setFixedHeight(self.scriptSpecs_tabs.tabBar(), 200)
        self.preview_tab = QtWidgets.QWidget()
        self.preview_tab.setObjectName("preview_tab")
        self.preview_Layout = QtWidgets.QGridLayout(self.preview_tab)
        self.preview_Layout.setObjectName("preview_Layout")
        self.preview_label = QLabel(self.preview_tab)
        self.preview_Layout.addWidget(self.preview_label, 0, 0, 1, 1)
        self.scriptSpecs_tabs.addTab(self.preview_tab, "")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.preview_label.setFont(font)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setObjectName("preview_label")
        self.description_tab = QtWidgets.QWidget()
        self.description_tab.setObjectName("description_tab")
        self.description_Layout = QtWidgets.QGridLayout(self.description_tab)
        self.description_Layout.setObjectName("description_Layout")
        self.description_textbrowser = QTextBrowser(self.description_tab)
        self.description_Layout.addWidget(self.description_textbrowser, 0, 0, 1, 1)
        self.description_textbrowser.setObjectName("description_textbrowser")
        self.description_textbrowser.setReadOnly(True)
        self.description_textbrowser.setOpenExternalLinks(True)
        self.scriptSpecs_tabs.addTab(self.description_tab, "")
        self.widgets_layout.addWidget(self.scriptSpecs_tabs, 1, 0, 7, 6)

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
        self.scripts_handler_pushButton = QPushButton2(self.centralwidget)
        self.scripts_handler_pushButton.setObjectName("scripts_handler_pushButton")
        self.widgets_layout.addWidget(self.scripts_handler_pushButton, 8, 2, 2, 1)
        self.scripts_handler_pushButton.clicked.connect(
            lambda: self.openScriptsHandlerWindow(self)
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

        self.overall_settings = get_settings()
        do_feeds_update = False
        last_check_str = self.overall_settings["Last feeds update"]
        if last_check_str != "":
            last_check = datetime.strptime(
                self.overall_settings["Last feeds update"], "%Y-%m-%d %H:%M:%S.%f"
            )
            now = datetime.now()
            time_difference = now - last_check
            if time_difference.days >= self.overall_settings["Automatic feeds update"]:
                do_feeds_update = True
        else:
            do_feeds_update = True
        if do_feeds_update:
            self.time_window = QtWidgets.QMainWindow()
            self.time_ui = Ui_ScriptsHandlerWindow()
            self.time_ui.setupUi(self.time_window, MainWindow)
            self.time_ui.update_feeds_process(self)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ScriptSelection_label.setText(_translate("MainWindow", "Select Script"))
        self.preview_label.setText(
            _translate("MainWindow", "No script selected to preview.")
        )
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.settings_pushButton.setText(_translate("MainWindow", "Settings"))
        self.scripts_handler_pushButton.setText(
            _translate("MainWindow", "Handle Scripts")
        )
        self.next_pushButton.setText(_translate("MainWindow", "Next"))
        self.LinesSelection_label.setText(_translate("MainWindow", "Apply script on:"))
        self.SelectedLines_radioButton.setText(
            _translate("MainWindow", "selected line(s)")
        )
        self.AllLines_radioButton.setText(_translate("MainWindow", "all lines"))
        self.scriptSpecs_tabs.setTabText(
            self.scriptSpecs_tabs.indexOf(self.preview_tab),
            _translate("MainWindow", "Preview"),
        )
        self.scriptSpecs_tabs.setTabText(
            self.scriptSpecs_tabs.indexOf(self.description_tab),
            _translate("MainWindow", "Details"),
        )

    def openSettingsWindow(self, MainWindow):
        window = QtWidgets.QMainWindow()
        ui = Ui_SettingsWindow()
        ui.setupUi(window, MainWindow)
        window.show()

    def openScriptsHandlerWindow(self, MainWindow):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_ScriptsHandlerWindow()
        self.ui.setupUi(self.window, MainWindow)
        self.window.show()

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
            self.description_textbrowser.setText(get_description(self.selected_script))
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
