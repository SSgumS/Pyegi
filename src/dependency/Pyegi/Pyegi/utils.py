import os
import json
import qdarktheme
from PyQt6.QtWidgets import QWidget
from enum import Enum
import toml
from os.path import exists
import urllib.request
from urllib.parse import quote, unquote
import requests
from bs4 import BeautifulSoup
import numpy as np
import shutil

utils_path = os.path.dirname(__file__)
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


def get_description(poetry_data, pyegi_data, attr, default_out=""):
    try:
        output = pyegi_data[attr]
    except:
        output = try_except(poetry_data, attr, default_out)
    return output


class script_pyegi_connection(object):
    def __init__(self, pyproject_file_path) -> None:
        self.describer_version = ""
        self.name = ""
        self.description = ""
        self.version = ""
        self.version_description = ""
        self.authors = []
        self.discoverable = True
        self.known_feeds = []
        if exists(pyproject_file_path):
            pyproject_data = toml.load(pyproject_file_path)
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


class github_decode(object):
    def __init__(self, url) -> None:
        url_split = url.split("/")
        script_name = unquote(url_split[-1])
        self.repo_name = "/".join(url_split[3:5])
        try:
            self.branch_name = url_split[6]
        except:
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
                        self.branch_name = url_temp[tree_indicator_len:]
                        break
                except:
                    pass
            url_split.append("tree")
            url_split.append(self.branch_name)

        try:
            self.prefix = "/" + "/".join(url_split[7:])
        except:
            self.prefix = ""

        try:
            pyproject_toml_path = "pyproject.toml"
            pyproject_toml_url = self.get_download_url(pyproject_toml_path, self.prefix)
            pyproject_toml_dir = temp_dir + "pyproject.toml"
            if exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            urllib.request.urlretrieve(pyproject_toml_url, pyproject_toml_dir)
            script_info = script_pyegi_connection(pyproject_toml_dir)
            self.script_name = script_info.name
        except:
            self.script_name = script_name
        if exists(temp_dir):
            shutil.rmtree(temp_dir)

        self.main_prefix_len = len("/" + "/".join(url_split[3:]))
        self.url = url

    def get_links(self, main_url):
        url_split = main_url.split("/")

        if len(url_split) <= 5:
            url_split.append("tree")
            url_split.append(self.branch_name)
        prefix = "/" + "/".join(url_split[3:])
        prefix_len = len(prefix)
        url_blob = url_split
        url_blob[5] = "blob"
        prefix_blob = "/" + "/".join(url_blob[3:])
        prefix_blob_len = len(prefix_blob)

        reqs = requests.get(main_url)
        soup = BeautifulSoup(reqs.text, "html.parser")

        dirs = []
        files = []
        links = []
        for link in soup.find_all("a"):
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
        while len(urls) > 0:
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
