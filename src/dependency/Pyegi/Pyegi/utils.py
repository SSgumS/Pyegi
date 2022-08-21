import os
import json
import qdarktheme
from PyQt6.QtWidgets import QWidget, QLineEdit, QComboBox, QCompleter
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from enum import Enum
import toml
from os.path import exists
import urllib.request
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from typing import List
from datetime import datetime
import copy


if exists(os.path.dirname(__file__) + "/development-indicator.dummy"):
    DEVELOPMENT_MODE = True
else:
    DEVELOPMENT_MODE = False
if DEVELOPMENT_MODE:
    print(">>>>>>>>>>  Development mode  <<<<<<<<<<")

utils_path = os.path.dirname(__file__)
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
settings_file_path = utils_path + "/settings.json"
themes_path = utils_path + "/Themes/"
temp_dir = utils_path + "/temp/"
feed_file_path = utils_path + "/scripts_feed.json"
pyproject_toml_path = "pyproject.toml"


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


def set_style(window: QWidget, theme: str = None) -> Theme:
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


def get_dict_attribute(data: dict, attr, default=""):
    try:
        output = data[attr]
    except:
        output = default
    if isinstance(output, (list, dict)):
        output = copy.deepcopy(output)
    return output


def get_pyegi_duplicated_field(poetry_data, pyegi_data, attr, default=""):
    output = get_dict_attribute(pyegi_data, attr, None)
    if not output:
        output = get_dict_attribute(poetry_data, attr, default)
    return output


def _get_description_value(data: dict, attr, theme: Theme):
    output = get_dict_attribute(data, attr)

    if theme == Theme.PYEGI:
        hyperlink_color = 'style="color: rgb(200, 200, 200);"'
    else:
        hyperlink_color = ""

    attr_to_version_description_map = {
        "version": "version-description",
        "latest version": "latest_version_description",
        "installed version": "installed_version_description",
    }
    for key in attr_to_version_description_map:
        if attr != key:
            continue
        version_description = get_dict_attribute(
            data, attr_to_version_description_map[attr]
        )
        if version_description != "":
            output = f"{version_description} ({output})"
        break

    if attr == "authors":
        try:
            for i, str in enumerate(output):
                output[i] = re.sub(
                    r"(.+?) ?<(.+)>",
                    f'<a {hyperlink_color} href="mailto:\\2">\\1</a>',
                    str,
                )
        except:
            pass
        output = "<span>[" + ", ".join(output) + "]</span>"
    elif attr == "url":
        output = f'<a {hyperlink_color} href="{output}">{output}</a>'

    return output


def _convert_to_header(str):
    return f"<b>{str}:</b>"


def get_textBrowser_description(data: dict, theme: Theme, desired_attributes=None):
    script_description = "<html>"
    description_values = []
    if not desired_attributes:
        desired_attributes = data.keys()
    for attr in desired_attributes:
        description_value = _get_description_value(data, attr, theme)
        description_values.append(description_value)
    headers = [_convert_to_header(str) for str in desired_attributes]
    for header, description_value in zip(headers, description_values):
        script_description += f"{header}<br>{description_value}<br><br>"
    script_description += "</html>"
    return script_description


def get_feed_file():
    if exists(feed_file_path):
        with open(feed_file_path) as file:
            feed_file = json.load(file)
    else:
        feed_file = {}
        with open(feed_file_path, "w") as file:
            json.dump(feed_file, file, indent=4)
    return feed_file


def download_file(url, local_path):
    with requests.get(url, stream=True) as r:
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=16 * 1024):
                f.write(chunk)


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


class ScriptPyProject:
    def __init__(self, pyproject_file_path=None, pyproject_text=None) -> None:
        if pyproject_file_path:
            pyproject_data = toml.load(pyproject_file_path)
        else:
            pyproject_data = toml.loads(pyproject_text)
        self.pyproject_data = pyproject_data
        poetry_data = get_dict_attribute(pyproject_data["tool"], "poetry")
        pyegi_data = get_dict_attribute(pyproject_data["tool"], "pyegi")
        self.describer_version = get_dict_attribute(
            pyegi_data, "describer-version", "0.1.0"
        )
        self.name = get_pyegi_duplicated_field(poetry_data, pyegi_data, "name")
        self.description = get_pyegi_duplicated_field(
            poetry_data, pyegi_data, "description"
        )
        self.version = get_pyegi_duplicated_field(poetry_data, pyegi_data, "version")
        self.version_description = get_dict_attribute(pyegi_data, "version-description")
        self.authors = get_pyegi_duplicated_field(
            poetry_data, pyegi_data, "authors", []
        )
        self.discoverable = get_dict_attribute(pyegi_data, "discoverable", True)
        self.known_feeds: List[str] = get_dict_attribute(pyegi_data, "known-feeds", [])
        for i in range(len(self.known_feeds)):
            self.known_feeds[i] = unquote(self.known_feeds[i])
        pyegi_data_files = get_dict_attribute(pyegi_data, "files")
        self.keep_files = get_dict_attribute(pyegi_data_files, "keep", [])

    def get_textBrowser_description(self, theme: Theme):
        return get_textBrowser_description(
            {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "version-description": self.version_description,
                "authors": self.authors,
            },
            theme,
            ["name", "description", "version", "authors"],
        )


class FeedParser:
    def __init__(self, url, parse=True) -> None:
        if url[:19] != "https://github.com/":
            url = "https://" + url[url.find("github.com/") :]
        self.url = unquote(url)
        url_split = self.url.split("/")
        if len(url_split) < 5:
            raise ValueError("Wrong feed url!")
        self.username = url_split[3]
        self.repo_name = "/".join(url_split[3:5])
        self.tags = []
        try:
            self.folder_path = "/".join(url_split[7:])
        except:
            self.folder_path = ""
        if self.folder_path != "":
            self.ID = self.repo_name + "/" + self.folder_path
        else:
            self.ID = self.repo_name + "/"

        self.is_parsed = False
        if parse:
            self._parse()

    def _parse(self):
        self.is_parsed = True

        url = self.url
        url_split = url.split("/")

        self.default_branch = self._get_main_branch_name()
        try:
            self.branch_name = url_split[6]
        except:
            self.branch_name = self.default_branch
            url_split.append("tree")
            url_split.append(self.branch_name)
            self.url = "/".join(url_split)

        self.script_info = self._get_script_info()
        self.script_name = self.script_info.name

        self._file_root_prefix_len = len(
            f"/{self.repo_name}/blob/{self.branch_name}/{self.folder_path}/"
        )
        self._dir_root_prefix_len = len(
            f"/{self.repo_name}/tree/{self.branch_name}/{self.folder_path}/"
        )

    def ensure_parsed(self):
        if not self.is_parsed:
            self._parse()

    def _get_main_branch_name(self):
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

    def _get_script_info(self):
        pyproject_toml_url = self.get_download_url(
            pyproject_toml_path, self.folder_path
        )
        response = requests.get(pyproject_toml_url)
        self.raw_datetime = self._get_pyproject_datetime_text()
        self.datetime = FeedParser.parse_datetime(self.raw_datetime)
        script_info = ScriptPyProject(pyproject_text=response.text)
        return script_info

    def _get_links(self, main_url):
        url_split = main_url.split("/")

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
        dir_links = []
        for link in soup.find_all("a", class_="js-navigation-open Link--primary"):
            url = unquote(link.get("href"))
            if url[:prefix_blob_len] == prefix_blob:
                files.append(url[self._file_root_prefix_len :])
            if (url[:prefix_len] == prefix) and (url != prefix):
                dirs.append(url[self._dir_root_prefix_len :])
                dir_links.append("https://github.com" + url)
        return dirs, files, dir_links

    def get_files_and_folders(self):
        self.ensure_parsed()
        urls = [self.url]
        folders = []
        files = []
        while urls:
            current_url = urls[0]
            dirs, filenames, dir_links = self._get_links(current_url)
            folders += dirs
            files += filenames
            urls += dir_links
            urls = urls[1:]

        # since we need folders variable to create folders
        # and we dont't want to use os.makedirs function more than needed
        # we try to exclude unnecessary folders

        folders.sort()
        folders_len = len(folders)
        # we need a list for extracting the indexes of the folders to be excluded
        to_be_removed = np.zeros(folders_len)

        for i in range(folders_len - 1):
            folder = folders[i]
            for j in range(i + 1, folders_len):
                folder2 = folders[j]
                if folder2[: len(folder)] == folder:
                    to_be_removed[i] = 1
                    break

        # now that we have the indexes, we remove the corresponding folders in a reversed mode
        # in order to avoid calculating the new indexes
        for i in reversed(np.nonzero(to_be_removed)[0]):
            folders.pop(i)

        return files, folders

    def get_download_url(self, file, folder_path=""):
        self.ensure_parsed()
        return f"https://raw.githubusercontent.com/{self.repo_name}/{self.branch_name}/{folder_path}/{file}"

    def _get_tags(self, url):
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

    def populate_tags(self):
        if self.tags:
            return

        url = self.url
        url_split = url.split("/")
        url = "/".join(url_split[:5]) + "/tags"

        tags = []
        more_tags = True
        url2 = url
        while more_tags:
            tags_temp = self._get_tags(url2)
            if tags_temp:
                tags += tags_temp
                url2 = url + "?after=" + tags_temp[-1]
            else:
                more_tags = False

        self.tags = tags

    def get_relevant_tags(self):
        if not self.tags:
            self.populate_tags()

        url = self.url
        url_split = url.split("/")
        if len(url_split) == 5:
            url_split.append("tree")
            url_split.append("")

        relevant_tags = []
        version_list = []
        version_description_list = []
        for tag in self.tags:
            url_split[6] = tag
            url = "/".join(url_split)
            g = FeedParser(url, False)
            pyproject_toml_url = f"https://raw.githubusercontent.com/{g.repo_name}/{tag}/{g.folder_path}/{pyproject_toml_path}"
            try:
                response = requests.get(pyproject_toml_url)
                script_info = ScriptPyProject(pyproject_text=response.text)
                version = script_info.version
                if version not in version_list:
                    relevant_tags.append(tag)
                    version_list.append(version)
                    version_description_list.append(script_info.version_description)
            except:
                pass
        self.relevant_tags = relevant_tags
        self.version_list = version_list
        self.version_description_list = version_description_list

    @classmethod
    def parse_datetime(cls, raw_datetime):
        return datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M:%SZ")

    def _get_pyproject_datetime_text(self) -> datetime:
        self.ensure_parsed()
        url_split = self.url.split("/")
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
        raise LookupError("No datetime found!")

    def is_main_branch(self):
        return self.branch_name == self.default_branch
