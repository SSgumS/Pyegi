from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QComboBox,
    QGridLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTextBrowser,
    QMessageBox,
)
import os
import json
from utils import set_style, get_settings, FeedParser, get_textBrowser_description
from installer import update_feeds, install_script, uninstall_script
from datetime import datetime
import traceback
import typing
import sys

if typing.TYPE_CHECKING:
    from main import Ui_MainWindow


utils_path = os.path.dirname(__file__)
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"
temp_dir = os.path.dirname(__file__) + "/temp/"
feed_file_path = os.path.dirname(__file__) + "/scripts_feed.json"


class ManageHiddenScriptsComboboxItems:
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
            g = FeedParser(url)
            isInstalled = False
            installation_attempts = 0
            while not isInstalled and installation_attempts < 2:
                try:
                    install_script(g)
                    isInstalled = True
                except:
                    print(traceback.format_exc())
                    uninstall_script(g.ID)
                    installation_attempts += 1
            if not isInstalled:
                print(f"Couldn't install '{g.script_name}'!")
        print("\nInstallation finished!")
        self.finished.emit()


class Ui_ScriptsHandlerWindow:
    def setupUi(self, window, main_ui: "Ui_MainWindow" = None):
        self.window = window
        self.main_ui = main_ui
        window.setObjectName("ScriptsHandlerWindow")
        window.resize(1280, 720)
        self.overall_settings = get_settings()
        self.theme = set_style(window, self.overall_settings["Theme"])
        self.centralwidget = QtWidgets.QWidget(window)
        self.centralwidget.setObjectName("centralwidget")
        self.window_layout = QGridLayout(self.centralwidget)
        self.window_layout.setObjectName("window_layout")
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setObjectName("widgets_layout")
        self.manage_hidden_scripts_combobox = QComboBox(self.centralwidget)
        self.manage_hidden_scripts_combobox.setObjectName(
            "manage_hidden_scripts_combobox"
        )
        ci = ManageHiddenScriptsComboboxItems()
        combobox_items = [ci.Installed, ci.Updatable, ci.All]
        self.manage_hidden_scripts_combobox.addItems(combobox_items)
        self.widgets_layout.addWidget(self.manage_hidden_scripts_combobox, 0, 0, 1, 1)
        self.manage_hidden_scripts_combobox.setCurrentText(ci.All)
        self.manage_hidden_scripts_combobox.currentTextChanged.connect(
            self.manage_hidden_scripts
        )

        self.update_feeds_pushButton = QPushButton(self.centralwidget)
        self.update_feeds_pushButton.setObjectName("update_feeds_pushButton")
        self.widgets_layout.addWidget(self.update_feeds_pushButton, 0, 1, 1, 1)
        self.update_feeds_pushButton.setMinimumWidth(80)
        self.update_feeds_pushButton.clicked.connect(self.update_feeds_process)

        self.search_scripts_lineedit = QLineEdit(self.centralwidget)
        self.search_scripts_lineedit.setObjectName("search_scripts_lineedit")
        self.widgets_layout.addWidget(self.search_scripts_lineedit, 0, 7, 1, 4)
        self.search_scripts_lineedit.setPlaceholderText("Search Scripts")
        self.search_scripts_lineedit.setMinimumWidth(250)
        self.search_scripts_lineedit.textChanged.connect(self.manage_hidden_scripts)

        self.description_textbrowser = QTextBrowser(self.centralwidget)
        self.description_textbrowser.setObjectName("description_textbrowser")
        self.widgets_layout.addWidget(self.description_textbrowser, 1, 11, 14, 5)
        self.description_textbrowser.setReadOnly(True)
        self.description_textbrowser.setOpenExternalLinks(True)

        self.install_pushButton = QPushButton(self.centralwidget)
        self.install_pushButton.setObjectName("install_pushButton")
        self.widgets_layout.addWidget(self.install_pushButton, 15, 15, 1, 1)
        self.install_pushButton.clicked.connect(self.install_checked_scripts)

        self.uninstall_pushButton = QPushButton(self.centralwidget)
        self.uninstall_pushButton.setObjectName("uninstall_pushButton")
        self.widgets_layout.addWidget(self.uninstall_pushButton, 15, 14, 1, 1)
        self.uninstall_pushButton.clicked.connect(self.uninstall_checked_scripts)

        self.close_pushButton = QPushButton(self.centralwidget)
        self.close_pushButton.setObjectName("close_pushButton")
        self.widgets_layout.addWidget(self.close_pushButton, 15, 0, 1, 1)
        self.close_pushButton.clicked.connect(lambda: window.close())

        spacerItem = QtWidgets.QSpacerItem(
            430,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.widgets_layout.addItem(spacerItem, 0, 2, 1, 1)

        self.window_layout.addLayout(self.widgets_layout, 0, 0, 1, 1)
        window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 308, 26))
        self.menubar.setObjectName("menubar")
        window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(window)
        self.statusbar.setObjectName("statusbar")
        window.setStatusBar(self.statusbar)

        self.retranslateUi(window)
        self.scripts_treeWidget_init()
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("ScriptsHandlerWindow", "Scripts Management"))
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
        self.scripts_treeWidget.itemSelectionChanged.connect(
            self.fetch_selected_script_info
        )
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
        self.fetch_selected_script_info()

    def update_feeds_process(self):
        self.thread = QThread()
        self.worker = Feed_Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.process_controls(True))
        self.thread.finished.connect(self.update_last_update_datetime)
        self.thread.finished.connect(
            lambda: self.update_feeds_pushButton.setText("Update feeds")
        )
        self.thread.finished.connect(
            lambda: self.main_ui.scripts_handler_pushButton.setText(
                "Scripts Management"
            )
        )

        self.process_controls(False)
        self.update_feeds_pushButton.setText("Updating...")
        self.main_ui.scripts_handler_pushButton.setText("Updating feeds...")
        self.thread.start()

    def process_controls(self, status):
        self.update_feeds_pushButton.setEnabled(status)
        self.main_ui.scripts_handler_pushButton.setEnabled(status)
        self.install_pushButton.setEnabled(status)
        self.uninstall_pushButton.setEnabled(status)
        if status:
            self.scripts_treeWidget_init()

    def update_last_update_datetime(self):
        now = datetime.now()
        self.overall_settings["Last feeds update"] = str(now)
        json.dump(self.overall_settings, open(settings_file_path, "w"))

    def fetch_selected_script_info(self):
        selected_item = self.scripts_treeWidget.selectedItems()
        if not selected_item:
            self.description_textbrowser.setText("")
            return

        selected_item = selected_item[0]
        for feed in self.feed_file:
            if selected_item == self.feed_file[feed]["treeWidgetItem"]:
                break
        desired_attributes = [
            "name",
            "description",
            "installed version",
            "latest version",
            "authors",
            "url",
        ]
        script_description = get_textBrowser_description(
            self.feed_file[feed],
            self.theme,
            desired_attributes,
        )
        self.description_textbrowser.setText(script_description)

    def _install_checked_scripts_parallel(self, urls):
        self.install_thread = QThread()
        self.install_worker = Installation_Worker(urls)
        self.install_worker.moveToThread(self.install_thread)
        self.install_thread.started.connect(self.install_worker.run)
        self.install_worker.finished.connect(self.install_thread.quit)
        self.install_worker.finished.connect(self.install_worker.deleteLater)
        self.install_thread.finished.connect(self.install_thread.deleteLater)
        self.install_thread.finished.connect(self.main_ui.repopulateCombobox)
        self.install_thread.finished.connect(lambda: self.process_controls(True))
        self.install_thread.finished.connect(
            lambda: self.install_pushButton.setText("Install/Update")
        )

        self.process_controls(False)
        self.install_pushButton.setText("Installing...")
        self.install_thread.start()

    def install_checked_scripts(self):
        urls = []
        for feed in self.feed_file:
            treeWidgetItem = self.feed_file[feed]["treeWidgetItem"]
            if (
                treeWidgetItem.checkState(0) == Qt.CheckState.Checked
                and not treeWidgetItem.isHidden()
                and self.feed_file[feed]["installation status"] != "completed"
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
        self._install_checked_scripts_parallel(urls)

    def uninstall_checked_scripts(self):
        verification = QMessageBox(self.centralwidget)
        verification.setText("Are you sure to uninstall the checked script(s)?")
        verification.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        verification.setIcon(QMessageBox.Icon.Question)
        verification.exec()
        if verification.clickedButton().text() == "&Yes":
            for feed in self.feed_file:
                treeWidgetItem = self.feed_file[feed]["treeWidgetItem"]
                if (
                    treeWidgetItem.checkState(0) == Qt.CheckState.Checked
                    and not treeWidgetItem.isHidden()
                    and self.feed_file[feed]["folder name"]
                ):
                    uninstall_script(feed)
            self.scripts_treeWidget_init()
            self.main_ui.repopulateCombobox()
            print("\nFinished uninstalling!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ScriptsHandlerWindow = QtWidgets.QMainWindow()
    ui = Ui_ScriptsHandlerWindow()
    ui.setupUi(ScriptsHandlerWindow)
    ScriptsHandlerWindow.show()
    sys.exit(app.exec())
