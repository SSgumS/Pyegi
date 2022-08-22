from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QPushButton,
    QComboBox,
    QCompleter,
    QGridLayout,
    QSizePolicy,
    QLabel,
    QRadioButton,
    QTextBrowser,
    QMainWindow,
)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QMovie
import os
import json
import sys
from settings import Ui_SettingsWindow
from scripts_handler import Ui_ScriptsHandlerWindow
from utils import (
    set_style,
    get_settings,
    ComboBoxLineEdit,
    ScriptPyProject,
)
from datetime import datetime
from typing import List


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

            # This part rotates the tabs' text so that they are not vertical.
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


class MainWindowComboboxEntry:
    def __init__(self, pyproject: ScriptPyProject, folder_name: str):
        self.pyproject = pyproject
        self.folder_name = folder_name


class Ui_MainWindow:
    def setupUi(self, window: QMainWindow):
        self.window = window
        window.setObjectName("MainWindow")
        window.resize(825, 600)
        self.theme = set_style(window)
        self.centralwidget = QtWidgets.QWidget(window)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.ScriptSelection_label = QLabel(self.centralwidget)
        self.ScriptSelection_label.setObjectName("ScriptSelection_label")
        self.widgets_layout.addWidget(self.ScriptSelection_label, 0, 0, 1, 1)

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
        self.preview_label.setFixedSize(self.preview_label.size())
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

        # combobox
        self.selected_script = None
        self.combobox = QComboBox(self.centralwidget)
        self.combobox.setObjectName("scriptNames_comboBox")
        self.widgets_layout.addWidget(self.combobox, 0, 1, 1, 5)
        self.combobox.setLineEdit(ComboBoxLineEdit(self.combobox))
        self.combobox.lineEdit().setPlaceholderText("Wait to load scripts...")
        self.combobox.currentIndexChanged.connect(self.preview)
        self.combobox.currentTextChanged.connect(self.textChangedHandler)
        self.repopulateCombobox()

        self.cancel_pushButton = QPushButton2(self.centralwidget)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.widgets_layout.addWidget(self.cancel_pushButton, 8, 0, 2, 1)
        self.cancel_pushButton.clicked.connect(QCoreApplication.instance().quit)
        self.settings_pushButton = QPushButton2(self.centralwidget)
        self.settings_pushButton.setObjectName("settings_pushButton")
        self.widgets_layout.addWidget(self.settings_pushButton, 8, 1, 2, 1)
        self.settings_pushButton.clicked.connect(self.openSettingsWindow)
        self.scripts_handler_pushButton = QPushButton2(self.centralwidget)
        self.scripts_handler_pushButton.setObjectName("scripts_handler_pushButton")
        self.widgets_layout.addWidget(self.scripts_handler_pushButton, 8, 2, 2, 1)
        self.scripts_handler_pushButton.clicked.connect(self.openScriptsHandlerWindow)
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
        window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 825, 26))
        self.menubar.setObjectName("menubar")
        window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(window)
        self.statusbar.setObjectName("statusbar")
        window.setStatusBar(self.statusbar)

        self.retranslateUi(window)
        QtCore.QMetaObject.connectSlotsByName(window)

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
            self.scripts_handler_window = QtWidgets.QMainWindow()
            self.scripts_handler_ui = Ui_ScriptsHandlerWindow()
            self.scripts_handler_ui.setupUi(self.scripts_handler_window, self)
            self.scripts_handler_ui.update_feeds_process()

    def retranslateUi(self, window):
        _translate = QCoreApplication.translate
        window.setWindowTitle(_translate("MainWindow", "Main Window"))
        self.ScriptSelection_label.setText(_translate("MainWindow", "Select Script"))
        self.preview_label.setText(
            _translate("MainWindow", "No script selected to preview.")
        )
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.settings_pushButton.setText(_translate("MainWindow", "Settings"))
        self.scripts_handler_pushButton.setText(
            _translate("MainWindow", "Scripts Management")
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

    def openSettingsWindow(self):
        self.child_window = QtWidgets.QMainWindow()
        self.child_ui = Ui_SettingsWindow()
        self.child_ui.setupUi(self.child_window, self)
        self.child_window.show()

    def openScriptsHandlerWindow(self):
        self.child_window = QtWidgets.QMainWindow()
        self.child_ui = Ui_ScriptsHandlerWindow()
        self.child_ui.setupUi(self.child_window, self)
        self.child_window.show()

    def writeMainWindowOutput(self):
        if not self.selected_script:
            return
        main_py_parameters = {}
        if self.AllLines_radioButton.isChecked():
            main_py_parameters["applyOn"] = "all lines"
        else:
            main_py_parameters["applyOn"] = "selected lines"
        main_py_parameters["selectedScript"] = self.selected_script.folder_name
        with open(system_inputs[1], "w") as file:
            json.dump(main_py_parameters, file, indent=4)
        QCoreApplication.instance().quit()

    def preview(self):
        if self.combobox.currentIndex() == -1:
            self.preview_label.setText("No script selected to preview.")
            self.selected_script = None
            self.description_textbrowser.setText("")
            return

        self.selected_script = self.combobox_items[self.combobox.currentIndex()]
        self.description_textbrowser.setText(
            self.selected_script.pyproject.get_textBrowser_description(self.theme)
        )

        main_gif_path = ""
        folder_name = self.selected_script.folder_name
        for file in os.listdir(scriptsPath + folder_name):
            if file.endswith(".gif"):
                main_gif_path = scriptsPath + folder_name + "/" + file
        if main_gif_path != "":
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(False)
            # self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            # print(self.movie.CacheMode(0))
            # self.movie.loopCount()
        else:
            self.preview_label.setText(
                f"No preview for {self.selected_script.pyproject.name}."
            )

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

    def repopulateCombobox(self):
        self.combobox.clear()
        combobox_items_name = []
        self.combobox_items: List[MainWindowComboboxEntry] = []
        for folder_name in os.listdir(scriptsPath):
            folder_path = os.path.join(scriptsPath, folder_name)
            if not os.path.isdir(folder_path):
                continue
            try:
                pyproject = ScriptPyProject(os.path.join(folder_path, "pyproject.toml"))
            except:
                continue
            self.combobox_items.append(MainWindowComboboxEntry(pyproject, folder_name))
            combobox_items_name.append(pyproject.name)
            self.combobox.addItem(pyproject.name)
        self.combobox.lineEdit().setPlaceholderText("Please select a script.")
        self.combobox.setCurrentIndex(-1)
        completer = QCompleter(combobox_items_name)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.combobox.setCompleter(completer)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
