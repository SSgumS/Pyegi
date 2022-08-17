from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QCoreApplication, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QComboBox,
    QGridLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTextBrowser,
    QMessageBox,
    QCompleter,
)
import os
import json
from utils import set_style, get_settings, github_decode, ComboBoxLineEdit
from installer import update_feeds, install_script, uninstall_script
import re
from datetime import datetime


utils_path = os.path.dirname(__file__)
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"
temp_dir = os.path.dirname(__file__) + "/temp/"
feed_file_path = os.path.dirname(__file__) + "/scripts_feed.json"


class manage_hidden_scripts_combobox_items(object):
    def __init__(self) -> None:
        self.Installed = "Installed"
        self.Updatable = "Updatable"
        self.All = "All"


class Feed_Worker(QObject):
    finished = pyqtSignal()

    def run(self):
        """Long-running task."""
        update_feeds()
        self.finished.emit()


class Installation_Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        for url in self.urls:
            g = github_decode(url)
            g.start()
            install_script(g)
        self.finished.emit()


class Ui_ScriptsHandlerWindow(object):
    def setupUi(self, ScriptsHandlerWindow, MainWindow=None):
        ScriptsHandlerWindow.setObjectName("ScriptsHandlerWindow")
        ScriptsHandlerWindow.resize(930, 500)
        self.overall_settings = get_settings()
        set_style(ScriptsHandlerWindow, self.overall_settings["Theme"])
        self.centralwidget = QtWidgets.QWidget(ScriptsHandlerWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.manage_hidden_scripts_combobox = QComboBox(self.centralwidget)
        self.manage_hidden_scripts_combobox.setObjectName(
            "manage_hidden_scripts_combobox"
        )
        ci = manage_hidden_scripts_combobox_items()
        combobox_items = [ci.Installed, ci.Updatable, ci.All]
        self.manage_hidden_scripts_combobox.addItems(combobox_items)
        self.widgets_layout.addWidget(self.manage_hidden_scripts_combobox, 0, 0, 1, 1)
        self.manage_hidden_scripts_combobox.setCurrentText(ci.Installed)
        self.manage_hidden_scripts_combobox.currentTextChanged.connect(
            lambda: self.manage_hidden_scripts()
        )

        self.update_feeds_pushButton = QPushButton(self.centralwidget)
        self.update_feeds_pushButton.setObjectName("update_feeds_pushButton")
        self.widgets_layout.addWidget(self.update_feeds_pushButton, 0, 1, 1, 1)
        self.update_feeds_pushButton.clicked.connect(
            lambda: self.update_feeds_process(MainWindow)
        )

        self.search_scripts_lineedit = QLineEdit(self.centralwidget)
        self.search_scripts_lineedit.setObjectName("search_scripts_lineedit")
        self.widgets_layout.addWidget(self.search_scripts_lineedit, 0, 10, 1, 1)
        self.search_scripts_lineedit.setPlaceholderText("Search Scripts")
        self.search_scripts_lineedit.textChanged.connect(
            lambda: self.manage_hidden_scripts()
        )

        self.description_textbrowser = QTextBrowser(self.centralwidget)
        self.description_textbrowser.setObjectName("description_textbrowser")
        self.widgets_layout.addWidget(self.description_textbrowser, 1, 11, 14, 5)
        self.description_textbrowser.setReadOnly(True)
        self.description_textbrowser.setOpenExternalLinks(True)

        self.install_pushButton = QPushButton(self.centralwidget)
        self.install_pushButton.setObjectName("install_pushButton")
        self.widgets_layout.addWidget(self.install_pushButton, 15, 15, 1, 1)
        self.install_pushButton.clicked.connect(
            lambda: self.install_checked_scripts(MainWindow)
        )

        self.uninstall_pushButton = QPushButton(self.centralwidget)
        self.uninstall_pushButton.setObjectName("uninstall_pushButton")
        self.widgets_layout.addWidget(self.uninstall_pushButton, 15, 14, 1, 1)
        self.uninstall_pushButton.clicked.connect(
            lambda: self.uninstall_checked_scripts(MainWindow)
        )

        self.close_pushButton = QPushButton(self.centralwidget)
        self.close_pushButton.setObjectName("close_pushButton")
        self.widgets_layout.addWidget(self.close_pushButton, 15, 0, 1, 1)
        self.close_pushButton.clicked.connect(lambda: ScriptsHandlerWindow.close())

        spacerItem = QtWidgets.QSpacerItem(
            430,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.widgets_layout.addItem(spacerItem, 0, 2, 1, 1)

        self.window_layout.addLayout(self.widgets_layout, 0, 0, 1, 1)
        ScriptsHandlerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ScriptsHandlerWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 308, 26))
        self.menubar.setObjectName("menubar")
        ScriptsHandlerWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ScriptsHandlerWindow)
        self.statusbar.setObjectName("statusbar")
        ScriptsHandlerWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ScriptsHandlerWindow)
        self.scripts_treeWidget_init()
        self.scripts_treeWidget.itemSelectionChanged.connect(
            lambda: self.fetch_script_info()
        )
        QtCore.QMetaObject.connectSlotsByName(ScriptsHandlerWindow)

    def retranslateUi(self, ScriptsHandlerWindow):
        _translate = QtCore.QCoreApplication.translate
        ScriptsHandlerWindow.setWindowTitle(
            _translate("ScriptsHandlerWindow", "MainWindow")
        )
        self.install_pushButton.setText(
            _translate("ScriptsHandlerWindow", "Install/Update")
        )
        self.uninstall_pushButton.setText(
            _translate("ScriptsHandlerWindow", "Uninstall")
        )
        self.close_pushButton.setText(_translate("ScriptsHandlerWindow", "Close"))
        self.update_feeds_pushButton.setText(
            _translate("ScriptsHandlerWindow", "Update feeds")
        )

    def scripts_treeWidget_init(self):
        _translate = QtCore.QCoreApplication.translate
        red_color = QtGui.QColor(255, 0, 0)
        self.scripts_treeWidget = QTreeWidget(self.centralwidget)
        self.scripts_treeWidget.setAlternatingRowColors(True)
        self.scripts_treeWidget.setObjectName("scripts_treeWidget")
        self.widgets_layout.addWidget(self.scripts_treeWidget, 1, 0, 14, 11)
        self.scripts_treeWidget.headerItem().setText(
            0, _translate("ScriptsHandlerWindow", "Name")
        )
        self.scripts_treeWidget.headerItem().setText(
            1, _translate("ScriptsHandlerWindow", "Description")
        )
        self.scripts_treeWidget.headerItem().setText(
            2, _translate("ScriptsHandlerWindow", "Installed Version")
        )
        self.scripts_treeWidget.headerItem().setText(
            3, _translate("ScriptsHandlerWindow", "Latest Version")
        )
        self.scripts_treeWidget.headerItem().setText(
            4, _translate("ScriptsHandlerWindow", "Available Tags")
        )

        try:
            f = open(feed_file_path)
            self.feed_file = json.load(f)
            f.close()
        except:
            self.feed_file = {}
        for feed in self.feed_file:
            treeWidgetItem = QTreeWidgetItem(self.scripts_treeWidget)
            treeWidgetItem.setText(
                0, _translate("ScriptsHandlerWindow", self.feed_file[feed]["name"])
            )
            treeWidgetItem.setText(
                1,
                _translate("ScriptsHandlerWindow", self.feed_file[feed]["description"]),
            )
            if self.feed_file[feed]["folder name"] != "":
                treeWidgetItem.setText(
                    2,
                    _translate(
                        "ScriptsHandlerWindow",
                        self.feed_file[feed]["installed version"],
                    ),
                )
                if self.feed_file[feed]["installation status"] != "completed":
                    treeWidgetItem.setForeground(2, red_color)
                    treeWidgetItem.setToolTip(
                        2, "This script is not installed properly!"
                    )
            else:
                pass
                # TODO: change the color/opacity of the text in the first column of this row if needed? (not done because we have the option of "Updatable" in the respective combobox)
            treeWidgetItem.setText(
                3,
                _translate(
                    "ScriptsHandlerWindow", self.feed_file[feed]["latest version"]
                ),
            )
            treeWidgetItem.setCheckState(0, Qt.CheckState.Unchecked)
            self.feed_file[feed]["treeWidgetItem"] = treeWidgetItem
            combobox = QComboBox(self.centralwidget)
            self.scripts_treeWidget.setItemWidget(treeWidgetItem, 4, combobox)
            if self.feed_file[feed]["tags"]:
                combobox.addItems(self.feed_file[feed]["tags"])
            self.feed_file[feed]["combobox"] = combobox
        for i in range(5):
            if i == 1:
                self.scripts_treeWidget.setColumnWidth(i, 200)
                continue
            self.scripts_treeWidget.resizeColumnToContents(i)
        self.scripts_treeWidget_checked = []
        self.install_pushButton.setEnabled(False)
        self.uninstall_pushButton.setEnabled(False)
        self.scripts_treeWidget.itemChanged.connect(self.treeWidgetItemChangeHandler)
        self.scripts_treeWidget.setSortingEnabled(True)
        self.manage_hidden_scripts()

    def treeWidgetItemChangeHandler(self, item, column_number):
        if column_number == 0:
            if item in self.scripts_treeWidget_checked:
                self.scripts_treeWidget_checked.remove(item)
                if not self.scripts_treeWidget_checked:
                    self.install_pushButton.setEnabled(False)
                    self.uninstall_pushButton.setEnabled(False)
            else:
                if not self.scripts_treeWidget_checked:
                    self.install_pushButton.setEnabled(True)
                    self.uninstall_pushButton.setEnabled(True)
                self.scripts_treeWidget_checked.append(item)

    def manage_hidden_scripts(self):
        hidden_state = self.manage_hidden_scripts_combobox.currentText()
        filter_term = self.search_scripts_lineedit.text().lower()
        for feed in self.feed_file:
            treeWidgetItem = self.feed_file[feed]["treeWidgetItem"]
            if hidden_state == "All":
                if filter_term in treeWidgetItem.text(0).lower():
                    treeWidgetItem.setHidden(False)
                else:
                    treeWidgetItem.setHidden(True)
            elif hidden_state == "Updatable":
                if treeWidgetItem.text(2) != "" and treeWidgetItem.text(
                    2
                ) != treeWidgetItem.text(3):
                    if filter_term in treeWidgetItem.text(0).lower():
                        treeWidgetItem.setHidden(False)
                    else:
                        treeWidgetItem.setHidden(True)
                else:
                    treeWidgetItem.setHidden(True)
            else:
                if treeWidgetItem.text(2) == "":
                    treeWidgetItem.setHidden(True)
                else:
                    if filter_term in treeWidgetItem.text(0).lower():
                        treeWidgetItem.setHidden(False)
                    else:
                        treeWidgetItem.setHidden(True)
        self.fetch_script_info()

    def update_feeds_process(self, MainWindow):
        # source: https://realpython.com/python-pyqt-qthread/
        self.thread = QThread()
        self.worker = Feed_Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.process_controls(MainWindow, False)
        self.update_feeds_pushButton.setText("Updating...")
        MainWindow.scripts_handler_pushButton.setText("Updating feeds...")
        self.thread.finished.connect(lambda: self.process_controls(MainWindow, True))
        self.thread.finished.connect(lambda: self.update_last_update_datetime())
        self.thread.finished.connect(
            lambda: self.update_feeds_pushButton.setText("Update feeds")
        )
        self.thread.finished.connect(
            lambda: MainWindow.scripts_handler_pushButton.setText("Handle Scripts")
        )

    def process_controls(self, MainWindow, Status):
        self.update_feeds_pushButton.setEnabled(Status)
        MainWindow.scripts_handler_pushButton.setEnabled(Status)
        self.install_pushButton.setEnabled(Status)
        self.uninstall_pushButton.setEnabled(Status)
        if Status:
            self.scripts_treeWidget_init()

    def update_last_update_datetime(self):
        now = datetime.now()
        self.overall_settings["Last feeds update"] = str(now)
        json.dump(self.overall_settings, open(settings_file_path, "w"))

    def convert_to_header(self, str):
        return f"<html><b>{str}:</b></html>"

    def fetch_script_info(self):
        selected_item = self.scripts_treeWidget.selectedItems()
        if selected_item:
            script_description = ""
            selected_item = selected_item[0]
            for feed in self.feed_file:
                if selected_item == self.feed_file[feed]["treeWidgetItem"]:
                    break
            desired_attributes = [
                "name",
                "description",
                "installed version",
                "latest version",
                "version_description",
                "authors",
            ]
            description_values = []
            for attr in desired_attributes:
                description_value = self.feed_file[feed][attr]
                if attr == "authors":
                    try:
                        for i, str in enumerate(description_value):
                            description_value[i] = re.sub(
                                "(.+) ?\<(.+)>", '<a href="mailto: \\2">\\1</a>', str
                            )
                    except:
                        pass
                description_values.append(description_value)
            headers = [self.convert_to_header(str) for str in desired_attributes]
            for header, description_value in zip(headers, description_values):
                script_description += f"{header}<br>{description_value}<br><br>"
            self.description_textbrowser.setText(script_description)
        else:
            self.description_textbrowser.setText("")

    def main_gui_combobox_handler(self, MainWindow):
        combobox_items = []
        MainWindow.combobox.clear()
        for script_name in os.listdir(scriptsPath):
            if not os.path.isdir(scriptsPath + script_name):
                continue
            MainWindow.combobox.addItem(script_name)
            combobox_items.append(script_name)
        MainWindow.combobox.setCurrentIndex(-1)
        MainWindow.completer = QCompleter(combobox_items)
        MainWindow.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        MainWindow.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        MainWindow.completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        MainWindow.combobox.setCompleter(MainWindow.completer)

    def install_checked_scripts_parallel(self, MainWindow, urls):
        self.install_thread = QThread()
        self.install_worker = Installation_Worker(urls)
        self.install_worker.moveToThread(self.install_thread)
        self.install_thread.started.connect(self.install_worker.run)
        self.install_worker.finished.connect(self.install_thread.quit)
        self.install_worker.finished.connect(self.install_worker.deleteLater)
        self.install_thread.finished.connect(self.install_thread.deleteLater)
        self.install_thread.finished.connect(
            lambda: self.main_gui_combobox_handler(MainWindow)
        )
        self.process_controls(MainWindow, False)
        self.install_pushButton.setText("Installing...")
        self.install_thread.finished.connect(
            lambda: self.process_controls(MainWindow, True)
        )
        self.install_thread.finished.connect(
            lambda: self.install_pushButton.setText("Install/Update")
        )
        self.install_thread.finished.connect(lambda: print("\nInstallation finished!"))
        self.install_thread.start()

    def install_checked_scripts(self, MainWindow):
        urls = []
        for feed in self.feed_file:
            treeWidgetItem = self.feed_file[feed]["treeWidgetItem"]
            if (
                treeWidgetItem.checkState(0) == Qt.CheckState.Checked
                and not treeWidgetItem.isHidden()
                and treeWidgetItem.text(2) != treeWidgetItem.text(3)
            ):
                url = self.feed_file[feed]["url"]
                combobox = self.feed_file[feed]["combobox"]
                selected_tag = combobox.currentText()
                if selected_tag != "":
                    url_split = url.split("/")
                    try:
                        url_split[6] = selected_tag
                    except:
                        url_split.append("tree")
                        url_split.append(selected_tag)
                    url = "/".join(url_split)
                urls.append(url)
        self.install_checked_scripts_parallel(MainWindow, urls)

    def uninstall_checked_scripts(self, MainWindow):
        verification = QMessageBox(self.centralwidget)
        verification.setText("Are you sure to uninstall the checked script(s)?")
        verification.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        verification.setIcon(QMessageBox.Icon.Question)
        verification.exec()
        # self.feed_file[feed]["treeWidgetItem"] = treeWidgetItem
        # self.feed_file[feed]["combobox"] = combobox
        if verification.clickedButton().text() == "&Yes":
            for feed in self.feed_file:
                treeWidgetItem = self.feed_file[feed]["treeWidgetItem"]
                if (
                    treeWidgetItem.checkState(0) == Qt.CheckState.Checked
                    and not treeWidgetItem.isHidden()
                    and self.feed_file[feed]["folder name"]
                ):
                    script = treeWidgetItem.text(0)
                    uninstall_script(script, feed)
            self.scripts_treeWidget_init()
            self.main_gui_combobox_handler(MainWindow)
            print("\nFinished uninstalling!")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ScriptsHandlerWindow = QtWidgets.QMainWindow()
    ui = Ui_ScriptsHandlerWindow()
    ui.setupUi(ScriptsHandlerWindow)
    ScriptsHandlerWindow.show()
    sys.exit(app.exec())
