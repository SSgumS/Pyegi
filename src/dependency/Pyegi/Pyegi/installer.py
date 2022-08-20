from multiprocessing.util import is_exiting
import os
from os.path import exists
import sys
import toml
import shutil
import csv
import json
import warnings
import urllib.request
import requests
from utils import (
    FeedParser,
    create_dirs,
    DEVELOPMENT_MODE,
    get_feed_file,
    ScriptPyProject,
    download_file,
)
from typing import List


pyproject_file = "pyproject.toml"
poetry_lock_file = "poetry.lock"
poetry_toml_file = "poetry.toml"
temp_dir = os.path.dirname(__file__) + "/temp/"
commons_dir = os.path.dirname(__file__) + "/commons/"
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
feed_file_path = os.path.dirname(__file__) + "/scripts_feed.json"
pyproject_file_path = dependency_dir + pyproject_file
# system_inputs = sys.argv
pyproject_file_url = (
    "https://raw.githubusercontent.com/SSgumS/Pyegi/main/pyproject.toml"
)
python_path = "C:/Python39/python.exe"


def path_process(path):
    connection_path = "/Lib/site-packages/"
    if path[:3] == "../":
        connection_path = "/Lib/"
        path = path[3:]
        if path[:3] == "../":
            connection_path = "/"
            path = path[3:]
    return path, connection_path


def create_poetry_toml(dir):
    if not exists(dir + poetry_toml_file):
        if not exists(dir):
            os.mkdir(dir)
        toml_file = open(dir + poetry_toml_file, "w")
        toml_file.write("[virtualenvs]\nin-project = true\n")
        toml_file.close()


def clean_lib_links(script):
    f = open(commons_dir + "lib_links.json")
    lib_links = json.load(f)
    f.close()
    pkgs = []
    zero_pkgs = []
    for package in lib_links["Packages"]:
        if script in package["Scripts"]:
            package["Scripts"].remove(script)
            if len(package["Scripts"]) == 0:
                if exists(commons_dir + package["Name"]):
                    zero_pkgs.append(package["Name"])
            else:
                pkgs.append(package)
        else:
            pkgs.append(package)
    lib_links["Packages"] = pkgs
    json.dump(lib_links, open(commons_dir + "lib_links.json", "w"))
    return zero_pkgs


def add_to_feed(feed: FeedParser, main_known_feeds: List[FeedParser]) -> List[str]:
    feed_file = get_feed_file()

    if not feed.script_info.discoverable:
        return []

    # prioritize main feeds
    for main_feed in main_known_feeds:
        if feed.ID == main_feed.ID and feed.url != main_feed.url:
            return []
    # prioritize existing feed in a special situation
    feed.populate_tags()
    if (
        (feed.ID in feed_file)
        and feed_file[feed.ID]["url"] != feed.url
        and (not feed.is_main_branch())
        and (not feed.tags)
        and (not feed_file[feed.ID]["is_main_branch"])
    ):
        date_time = feed.datetime
        local_date_time = FeedParser.parse_datetime(feed_file[feed.ID]["raw_datetime"])
        if feed_file[feed.ID]["is_main_branch"] or local_date_time > date_time:
            try:
                feed = (FeedParser(feed_file[feed.ID]["url"]),)
            except:
                pass

    # update feed file entry
    try:
        folder_name = feed_file[feed.ID]["folder name"]
        installed_version = feed_file[feed.ID]["installed version"]
        installed_version_description = feed_file[feed.ID][
            "installed_version_description"
        ]
        installation_status = feed_file[feed.ID]["installation status"]
    except:
        folder_name = ""
        installed_version = ""
        installed_version_description = ""
        installation_status = ""
    script_info = feed.script_info
    feed_file[feed.ID] = {
        "id": feed.ID,
        "url": feed.url,
        "name": script_info.name,
        "description": script_info.description,
        "latest version": script_info.version,
        "latest_version_description": script_info.version_description,
        "authors": script_info.authors,
        "tags": feed.tags,
        "is_main_branch": feed.is_main_branch(),
        "folder name": folder_name,
        "installed version": installed_version,
        "installed_version_description": installed_version_description,
        "installation status": installation_status,
    }

    # update feed file
    with open(feed_file_path, "w") as file:
        json.dump(feed_file, file)

    return script_info.known_feeds


def update_feeds():
    if DEVELOPMENT_MODE:
        pyegi_info = ScriptPyProject(pyproject_file_path)
    else:
        response = requests.get(pyproject_file_url)
        pyegi_info = ScriptPyProject(pyproject_text=response.text)
    checked_urls = []
    urls = pyegi_info.known_feeds
    main_known_feeds = [FeedParser(url, False) for url in urls]
    while urls:
        url = urls[0]
        try:
            g = FeedParser(url)
        except:
            urls = urls[1:]
            continue
        url = g.url
        checked_urls.append(url)
        known_feeds = add_to_feed(g, main_known_feeds)
        for known_feed in known_feeds:
            if (known_feed not in checked_urls) and g.is_url(known_feed):
                urls.append(known_feed)
        urls = urls[1:]


def download_script(g: FeedParser):
    script = g.script_name

    with open(feed_file_path) as file:
        feed_file = json.load(file)
    # folder name
    initial_folder_name = feed_file[g.ID]["folder name"]
    if initial_folder_name == "":
        initial_folder_name = script
        folder_name = initial_folder_name
        # current dirs that exist
        current_folders = []
        all_sub_objects = os.listdir(scriptsPath)
        for entry in all_sub_objects:
            path = os.path.join(scriptsPath, entry)
            if os.path.isdir(path):
                current_folders.append(entry)
        # choose folder name
        i = 1
        while folder_name in current_folders:
            folder_name = f"{initial_folder_name}_{i}"
            i += 1
        feed_file[g.ID]["folder name"] = folder_name
    else:
        folder_name = initial_folder_name
    # version
    feed_file[g.ID]["installed version"] = g.script_info.version
    feed_file[g.ID]["installed_version_description"] = g.script_info.version_description

    print(f"Preparing {script} links...")
    files, folders = g.get_files_and_folders()

    print(f"Creating {script} directories...")
    script_path = scriptsPath + folder_name + "/"
    for folder in folders:
        path = os.path.join(script_path, folder)
        if not exists(path):
            os.makedirs(path)
    if not exists(script_path):
        os.makedirs(script_path)
    feed_file[g.ID]["installation status"] = "directories created"
    with open(feed_file_path, "w") as file:
        json.dump(feed_file, file)

    print(f"Downloading {script} files...")
    for file in files:
        file_download_url = g.get_download_url(file, g.folder_path)
        path = f"{script_path}{file}"
        if (file not in g.script_info.keep_files) or (not exists(path)):
            download_file(file_download_url, path)
    feed_file[g.ID]["installation status"] = "downloaded"
    with open(feed_file_path, "w") as file:
        json.dump(feed_file, file)


def install_pkgs(g: FeedParser):
    script = g.script_name
    print(f"Processing {script} dependencies...")
    f = open(feed_file_path)
    feed_file = json.load(f)
    f.close()
    folder_name = feed_file[g.ID]["folder name"]
    script_path = scriptsPath + folder_name + "/"
    zero_pkgs = []
    if exists(script_path + pyproject_file):
        # renew temp folder
        create_poetry_toml(temp_dir)
        # cleanup script path
        if exists(script_path + poetry_lock_file):
            os.remove(script_path + poetry_lock_file)
        if exists(script_path + ".venv"):
            shutil.rmtree(script_path + ".venv")
            # removing script from lib_links
            zero_pkgs = clean_lib_links(g.ID)
        create_poetry_toml(script_path)
        # start installing process
        os.chdir(script_path)
        os.system(f"{python_path} -m poetry lock")
        src = script_path + pyproject_file
        dst = temp_dir + pyproject_file
        shutil.copyfile(src, dst)
        src = script_path + poetry_lock_file
        dst = temp_dir + poetry_lock_file
        shutil.copyfile(src, dst)
        os.chdir(temp_dir)
        os.system(f"{python_path} -m poetry lock --no-update")
        lock_content = toml.load(poetry_lock_file)
        packages = lock_content["package"]
        new_packages = []
        for package in packages:
            if package["category"] != "main":
                continue
            name_in_commons = f"{package['name']}-{package['version']}"
            try:
                zero_pkgs.remove(name_in_commons)
            except:
                pass
            # update lib_links
            f = open(commons_dir + "lib_links.json")
            lib_links = json.load(f)
            f.close()
            is_new_package = True
            for pkg in lib_links["Packages"]:
                if pkg["Name"] == name_in_commons:
                    pkg["Scripts"].append(g.ID)
                    is_new_package = False
            if is_new_package:
                lib_link = {}
                lib_link["Name"] = name_in_commons
                lib_link["Scripts"] = [g.ID]
                lib_links["Packages"].append(lib_link)
            json.dump(lib_links, open(commons_dir + "lib_links.json", "w"))
            # check if the package is already in commons
            dir_exist = os.path.isdir(commons_dir + name_in_commons)
            if dir_exist:
                filename = f"{commons_dir + name_in_commons}/Lib/site-packages/{name_in_commons}.dist-info/RECORD"
                with open(filename, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        path = row[0]
                        path, connection_path = path_process(path)
                        src = commons_dir + name_in_commons + connection_path + path
                        dst = f"{temp_dir}.venv{connection_path + path}"
                        create_dirs(dst)
                        os.link(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        create_dirs(dst)
                        os.link(src, dst)
            else:
                new_packages.append(name_in_commons)

        os.chdir(temp_dir)
        os.system(f"{python_path} -m poetry install --no-dev")
        for name_in_commons in new_packages:
            filename = (
                f"{temp_dir}.venv/Lib/site-packages/{name_in_commons}.dist-info/RECORD"
            )
            if exists(filename):
                with open(filename, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        path = row[0]
                        path, connection_path = path_process(path)
                        src = f"{temp_dir}.venv{connection_path + path}"
                        dst = commons_dir + name_in_commons + connection_path + path
                        create_dirs(dst)
                        if filename == src:
                            shutil.copy(src, dst)
                        else:
                            shutil.move(src, dst)
                        dst2 = f"{script_path}.venv{connection_path + path}"
                        create_dirs(dst2)
                        os.link(dst, dst2)
            else:
                warnings.warn(f"Package {name_in_commons} didn't have any RECORD file.")
        os.chdir(os.path.dirname(__file__))
        # removing temp dir
        shutil.rmtree(temp_dir)
        # remove unused packages from commons
        for zero_pkg in zero_pkgs:
            shutil.rmtree(commons_dir + zero_pkg)
        feed_file[g.ID]["installation status"] = "completed"
    else:
        print(
            f'The file "{pyproject_file}" doesn\'t exist in {script} script directory.'
        )
        feed_file[g.ID]["installation status"] = "not installed"
    with open(feed_file_path, "w") as file:
        json.dump(feed_file, file)


def install_script(g):
    download_script(g)
    install_pkgs(g)


def uninstall_script(feed_id):
    with open(feed_file_path) as file:
        feed_file = json.load(file)
    print(f"Processing {feed_file[feed_id]['name']} dependencies...")
    folder_name = feed_file[feed_id]["folder name"]
    if folder_name:
        script_path = scriptsPath + folder_name + "/"
        try:
        shutil.rmtree(script_path)
        except FileNotFoundError:
            pass
    zero_pkgs = clean_lib_links(feed_id)
    for zero_pkg in zero_pkgs:
        try:
        shutil.rmtree(commons_dir + zero_pkg)
        except FileNotFoundError:
            pass
    feed_file[feed_id]["folder name"] = ""
    feed_file[feed_id]["installed version"] = ""
    feed_file[feed_id]["installed_version_description"] = ""
    with open(feed_file_path, "w") as file:
        json.dump(feed_file, file)


if __name__ == "__main__":
    scripts_names = [
        name
        for name in os.listdir(scriptsPath)
        if os.path.isdir(os.path.join(scriptsPath, name))
    ]
    # url = "https://github.com/python-poetry/poetry-core/tree/1.1.0a6"
    url = "https://github.com/SSgumS/Pyegi/tree/download_script/src/dependency/Pyegi/PythonScripts/%5Bsample%5D%20ColorMania"
    g = FeedParser(url)
    # install_script(g)
    # download_script(g)
    # for script in scripts_names:
    #     install_pkgs(script)
    # update_feeds()
