import os
import json
import qdarktheme
from PyQt6.QtWidgets import QWidget, QLineEdit, QComboBox, QCompleter
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from enum import Enum
import toml
from os.path import exists
import urllib.request
from urllib.parse import quote, unquote
import requests
from bs4 import BeautifulSoup
import numpy as np
import re

utils_path = os.path.dirname(__file__)
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"
temp_dir = utils_path + "/temp/"


class Theme(Enum):
    PYEGI = "Pyegi"
    DARK = "Dark"
    LIGHT = "Light"
    SYSTEM = "System Default"


def get_settings():
    f = open(settings_file_path)
    overall_settings = json.load(f)
    f.close()
    return overall_settings


def set_style(window: QWidget, theme: str = None):
    if not theme:
        # load theme
        overall_settings = get_settings()
        theme = overall_settings["Theme"]
    theme: Theme = Theme(theme)
    # set theme
    if theme == Theme.DARK:
        window.setStyleSheet(qdarktheme.load_stylesheet())
    elif theme == Theme.LIGHT:
        window.setStyleSheet(qdarktheme.load_stylesheet("light"))
    elif theme == Theme.SYSTEM:
        window.setStyleSheet("")
    else:
        f = open(f"{themes_path}{theme.value}.css", "r")
        theme_data = f.read()
        f.close()
        window.setStyleSheet(theme_data)
    return theme


def create_dirs(path):
    parent, _ = os.path.split(path)
    if not exists(parent):
        os.makedirs(parent)


def try_except(data, attr, default_out=""):
    try:
        output = data[attr]
    except:
        output = default_out
    return output


def get_description_value(poetry_data, pyegi_data, attr, theme):
    try:
        output = pyegi_data[attr]
    except:
        output = try_except(poetry_data, attr)
    if attr == "version":
        try:
            output2 = pyegi_data["version-description"]
        except:
            output2 = try_except(poetry_data, "version-description")
        if output2 != "":
            output = f"{output2} ({output})"
    if attr == "installed version":
        try:
            output2 = pyegi_data["version_description"]
        except:
            output2 = try_except(poetry_data, "version_description")
        if output2 != "":
            output = f"{output2} ({output})"
    if attr == "authors":
        if theme == Theme.PYEGI:
            hyperlink_color = 'style="color: rgb(200, 200, 200)"'
        else:
            hyperlink_color = ""
        try:
            for i, str in enumerate(output):
                output[i] = re.sub(
                    "(.+) ?\<(.+)>",
                    f'<a {hyperlink_color} href="mailto: \\2">\\1</a>',
                    str,
                )
        except:
            pass
    return output


def convert_to_header(str):
    return f"<html><b>{str}:</b></html>"


def get_textBrowser_description(script_name, theme):
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
            "authors",
        ]
        description_values = []
        for attr in desired_attributes:
            description_value = get_description_value(
                poetry_data, pyegi_data, attr, theme
            )
            description_values.append(description_value)
        headers = [convert_to_header(str) for str in desired_attributes]
        for header, description_value in zip(headers, description_values):
            script_description += f"{header}<br>{description_value}<br><br>"
    return script_description


def get_description(poetry_data, pyegi_data, attr, default_out=""):
    try:
        output = pyegi_data[attr]
    except:
        output = try_except(poetry_data, attr, default_out)
    return output


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


class script_pyegi_connection(object):
    def __init__(self, pyproject_file_path, datetime, is_dir=True) -> None:
        self.describer_version = ""
        self.name = ""
        self.description = ""
        self.version = ""
        self.version_description = ""
        self.authors = []
        self.discoverable = True
        self.known_feeds = []
        self.keep_files = []
        self.datetime = datetime
        if is_dir:
            if not exists(pyproject_file_path):
                return
            pyproject_data = toml.load(pyproject_file_path)
        else:
            try:
                pyproject_data = toml.loads(pyproject_file_path)
            except:
                return
        poetry_data = try_except(pyproject_data["tool"], "poetry")
        pyegi_data = try_except(pyproject_data["tool"], "pyegi")
        self.describer_version = try_except(pyegi_data, "describer-version")
        self.name = get_description(poetry_data, pyegi_data, "name")
        self.description = get_description(poetry_data, pyegi_data, "description")
        self.version = get_description(poetry_data, pyegi_data, "version")
        self.version_description = try_except(pyegi_data, "version-description")
        self.authors = get_description(poetry_data, pyegi_data, "authors", [])
        self.discoverable = try_except(pyegi_data, "discoverable", True)
        self.known_feeds = try_except(pyegi_data, "known-feeds", [])
        pyegi_data_files = try_except(pyegi_data, "files")
        self.keep_files = try_except(pyegi_data_files, "keep", [])


class github_decode(object):
    def __init__(self, url) -> None:
        self.url = url
        url_split = url.split("/")
        self.repo_name = "/".join(url_split[3:5])
        self.tags = []
        try:
            self.ID = "/".join(url_split[3:5]) + "/" + "/".join(url_split[7:])
        except:
            self.ID = "/".join(url_split[3:5])

    def start(self):
        url = self.url
        url_split = url.split("/")
        script_name = unquote(url_split[-1])
        self.repo_name = "/".join(url_split[3:5])
        self.default_branch = self.main_branch_name()
        try:
            self.branch_name = url_split[6]
        except:
            self.branch_name = self.default_branch
            url_split.append("tree")
            url_split.append(self.branch_name)

        try:
            self.prefix = "/" + "/".join(url_split[7:])
        except:
            self.prefix = ""

        try:
            self.script_info = self.get_script_info()
            self.script_name = self.script_info.name
        except:
            self.script_name = script_name
            self.script_info = ""

        self.main_prefix_len = len("/" + "/".join(url_split[3:]))

    def resolve_url(self):
        self.get_all_tags()
        if self.tags:
            url = self.url
            url_split = url.split("/")
            if len(url_split) == 5:
                url_split.append("tree")
                url_split.append(self.tags[0])
            else:
                url_split[6] = self.tags[0]
            url = "/".join(url_split)
            if self.is_url(url):
                self.url = url

    def is_url(self, url):
        try:
            urllib.request.urlopen(url)
            return True
        except:
            try:
                url = "https://www.google.com/"
                urllib.request.urlopen(url)
                return False
            except:
                raise ValueError("You are not connected to the internet!")

    def main_branch_name(self):
        url = self.url
        url_split = url.split("/")
        url = "/".join(url_split[:5])
        tree_indicator = (
            f"/{self.repo_name}/hovercards/citation/sidebar_partial?tree_name="
        )
        tree_indicator_len = len(tree_indicator)
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, "html.parser")
        for link in soup.find_all("include-fragment"):
            url_temp = link.get("src")
            try:
                if url_temp[:tree_indicator_len] == tree_indicator:
                    branch_name = url_temp[tree_indicator_len:]
                    break
            except:
                pass
        return branch_name

    def get_script_info(self):
        pyproject_toml_path = "pyproject.toml"
        pyproject_toml_url = self.get_download_url(pyproject_toml_path, self.prefix)
        reqs = requests.get(pyproject_toml_url)
        datetime = self.get_pyproject_datetime(self.url)
        script_info = script_pyegi_connection(reqs.text, datetime, False)
        return script_info

    def get_links(self, main_url):
        url_split = main_url.split("/")

        if len(url_split) == 5:
            url_split.append("tree")
            url_split.append(self.branch_name)
        prefix = "/" + "/".join(url_split[3:])
        prefix_len = len(prefix)
        url_blob = url_split
        url_blob[5] = "blob"
        prefix_blob = "/" + "/".join(url_blob[3:])
        prefix_blob_len = len(prefix_blob)

        url_split[5] = "file-list"
        main_url = "/".join(url_split)

        reqs = requests.get(main_url)
        soup = BeautifulSoup(reqs.text, "html.parser")

        dirs = []
        files = []
        links = []
        for link in soup.find_all("a", class_="js-navigation-open Link--primary"):
            url = link.get("href")
            if url[:prefix_blob_len] == prefix_blob:
                files.append(unquote(url[self.main_prefix_len + 1 :]))
            if (url[:prefix_len] == prefix) and (url != prefix):
                dirs.append(unquote(url[self.main_prefix_len + 1 :]) + "/")
                links.append("https://github.com" + url)
        return dirs, files, links

    def get_files_and_folders(self):
        urls = [self.url]
        folders = []
        files = []
        while urls:
            current_url = urls[0]
            dirs, filenames, links = self.get_links(current_url)
            folders += dirs
            files += filenames
            urls += links
            urls = urls[1:]

        folders.sort()
        folders_len = len(folders)
        to_be_removed = np.zeros(folders_len)

        for i in range(folders_len - 1):
            folder = folders[i]
            for j in range(i + 1, folders_len):
                folder2 = folders[j]
                if folder2[: len(folder)] == folder:
                    to_be_removed[i] = 1
                    break

        for i in reversed(np.nonzero(to_be_removed)[0]):
            folders.pop(i)

        return files, folders

    def get_download_url(self, file, prefix=""):
        return f"https://raw.githubusercontent.com/{self.repo_name}/{self.branch_name}{prefix}/{quote(file)}"

    def get_tags(self, url):
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, "html.parser")
        tags = []
        for div in soup.find_all("div", class_="commit js-details-container Details"):
            sub_div = div.find("div", class_="d-flex")
            link_section = sub_div.find("a")
            link = link_section.get("href")
            url_split = link.split("/")
            tag = url_split[-1]
            tags.append(tag)
        return tags

    def get_all_tags(self):
        url = self.url
        url_split = url.split("/")
        url = "/".join(url_split[:5]) + "/tags"

        tags = []
        more_tags = True
        url2 = url
        while more_tags:
            tags_temp = self.get_tags(url2)
            if tags_temp:
                tags += tags_temp
                url2 = url + "?after=" + tags_temp[-1]
            else:
                more_tags = False

        self.tags = tags

    def get_pyproject_datetime(self, url):
        url_split = url.split("/")
        if len(url_split) == 5:
            url_split.append("tree")
            url_split.append(self.default_branch)
        url_split[5] = "file-list"
        url = "/".join(url_split)
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, "html.parser")
        for div in soup.find_all(
            "div",
            class_="Box-row Box-row--focus-gray py-2 d-flex position-relative js-navigation-item",
        ):
            subdiv = div.find("a", title="pyproject.toml")
            if subdiv:
                time_div = div.find("time-ago")
                return time_div.get("datetime")
