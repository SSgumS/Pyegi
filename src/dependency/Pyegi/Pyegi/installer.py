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
from utils import github_decode, create_dirs
from datetime import datetime


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
development_check_file_path = (
    os.path.dirname(__file__) + "/kl342klfdsf.3244dsffger+_Fwr_@2dsa2@.k3f"
)
if exists(development_check_file_path):
    development_mode = True
else:
    development_mode = False
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


def feed_details(g):
    url = g.url
    script_info = g.script_info
    is_main_brabch = g.branch_name == g.default_branch
    g.get_all_tags()
    return {
        "url": url,
        "name": script_info.name,
        "description": script_info.description,
        "latest version": script_info.version,
        "version_description": script_info.version_description,
        "authors": script_info.authors,
        "tags": g.tags,
        "is_main_branch": is_main_brabch,
    }


def assign_feed(
    feed_file,
    g,
    folder_name,
    version,
    installed_version_description,
    installation_status,
):
    feed_file[g.ID] = feed_details(g)
    feed_file[g.ID]["folder name"] = folder_name
    feed_file[g.ID]["installed version"] = version
    feed_file[g.ID]["installed_version_description"] = installed_version_description
    feed_file[g.ID]["installation status"] = installation_status


def get_IDs(urls):
    IDs = []
    for url in urls:
        g = github_decode(url)
        IDs.append(g.ID)
    return IDs


def add_to_feed(url, pyegi_info):
    main_known_feeds = pyegi_info["known-feeds"]
    main_known_feeds_IDs = get_IDs(main_known_feeds)
    if exists(feed_file_path):
        f = open(feed_file_path)
        feed_file = json.load(f)
        f.close()
    else:
        feed_file = {}
    g = github_decode(url)
    g.start()
    script_info = g.script_info
    if script_info == "":
        return []
    if script_info.discoverable == True:
        try:
            folder_name = feed_file[g.ID]["folder name"]
            version = feed_file[g.ID]["installed version"]
            installed_version_description = feed_file[g.ID][
                "installed_version_description"
            ]
            installation_status = feed_file[g.ID]["installation status"]
        except:
            folder_name = ""
            version = ""
            installed_version_description = ""
            installation_status = ""
        if g.tags:
            assign_feed(
                feed_file,
                g,
                folder_name,
                version,
                installed_version_description,
                installation_status,
            )
        else:
            if g.ID in main_known_feeds_IDs:
                idx = main_known_feeds_IDs.index(g.ID)
                if main_known_feeds[idx] == url:
                    assign_feed(
                        feed_file,
                        g,
                        folder_name,
                        version,
                        installed_version_description,
                        installation_status,
                    )
            else:
                if (g.ID not in feed_file) or (g.branch_name == g.default_branch):
                    assign_feed(
                        feed_file,
                        g,
                        folder_name,
                        version,
                        installed_version_description,
                        installation_status,
                    )
                else:
                    if not feed_file[g.ID]["is_main_branch"]:
                        date_time = datetime.strptime(
                            script_info.datetime, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        local_date_time = datetime.strptime(
                            g.get_pyproject_datetime(feed_file[g.ID]["url"]),
                            "%Y-%m-%dT%H:%M:%SZ",
                        )
                        if date_time > local_date_time:
                            assign_feed(
                                feed_file,
                                g,
                                folder_name,
                                version,
                                installed_version_description,
                                installation_status,
                            )
    json.dump(feed_file, open(feed_file_path, "w"))
    return script_info.known_feeds


def update_feeds():
    if development_mode:
        pyproject_contents = toml.load(pyproject_file_path)
    else:
        response = urllib.request.get(pyproject_file_url)
        pyproject_contents = toml.loads(response.text)
    pyegi_info = pyproject_contents["tool"]["pyegi"]
    checked_urls = []
    urls = pyegi_info["known-feeds"]
    while urls:
        url = urls[0]
        if url[:19] != "https://github.com/":
            url = "https://" + url[url.find("github.com/") :]
        url_split = url.split("/")
        if len(url_split) < 5:
            urls = urls[1:]
            continue
        checked_urls.append(url)
        g = github_decode(url)
        g.resolve_url()
        url = g.url
        known_feeds = add_to_feed(url, pyegi_info)
        for known_feed in known_feeds:
            if (known_feed not in checked_urls) and g.is_url(known_feed):
                urls.append(known_feed)
        urls = urls[1:]


def download_script(g):
    script = g.script_name
    print(f"Preparing {script} links...")
    files, folders = g.get_files_and_folders()
    f = open(feed_file_path)
    feed_file = json.load(f)
    f.close()
    initial_folder_name = feed_file[g.ID]["folder name"]
    if initial_folder_name == "":
        initial_folder_name = script
        folder_name = initial_folder_name
        new_folder_name = folder_name
        i = 2
        is_exiting_name = True
        while is_exiting_name:
            for feed in feed_file:
                if folder_name.lower() == feed_file[feed]["folder name"].lower():
                    new_folder_name = initial_folder_name + f"_{i}"
                    continue
            if new_folder_name == folder_name:
                is_exiting_name = False
            else:
                folder_name = new_folder_name
            i += 1
        feed_file[g.ID]["folder name"] = folder_name
    else:
        folder_name = initial_folder_name
    feed_file[g.ID]["installed version"] = g.script_info.version
    feed_file[g.ID]["installed_version_description"] = g.script_info.version_description
    script_path = scriptsPath + folder_name + "/"
    for folder in folders:
        path = script_path + folder
        if not exists(path):
            os.makedirs(path)

    if not exists(script_path):
        os.makedirs(script_path)

    print(f"Downloading {script}...")
    for file in files:
        file_download_url = g.get_download_url(file, g.prefix)
        file_name = f"{script_path}{file}"
        if (file not in g.script_info.keep_files) or (not exists(file_name)):
            urllib.request.urlretrieve(file_download_url, file_name)
    feed_file[g.ID]["installation status"] = "downloaded"
    json.dump(feed_file, open(feed_file_path, "w"))


def install_pkgs(g):
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
            zero_pkgs = clean_lib_links(script)
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
                    pkg["Scripts"].append(script)
                    is_new_package = False
            if is_new_package:
                lib_link = {}
                lib_link["Name"] = name_in_commons
                lib_link["Scripts"] = [script]
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
    json.dump(feed_file, open(feed_file_path, "w"))


def install_script(g):
    download_script(g)
    install_pkgs(g)


def uninstall_script(script, ID):
    print(f"Processing {script} dependencies...")
    f = open(feed_file_path)
    feed_file = json.load(f)
    f.close()
    folder_name = feed_file[ID]["folder name"]
    if folder_name:
        script_path = scriptsPath + folder_name + "/"
        shutil.rmtree(script_path)
    zero_pkgs = clean_lib_links(script)
    for zero_pkg in zero_pkgs:
        shutil.rmtree(commons_dir + zero_pkg)
    feed_file[ID]["folder name"] = ""
    feed_file[ID]["installed version"] = ""
    feed_file[ID]["installed_version_description"] = ""
    json.dump(feed_file, open(feed_file_path, "w"))


if __name__ == "__main__":
    scripts_names = [
        name
        for name in os.listdir(scriptsPath)
        if os.path.isdir(os.path.join(scriptsPath, name))
    ]
    # url = "https://github.com/python-poetry/poetry-core/tree/1.1.0a6"
    url = "https://github.com/SSgumS/Pyegi/tree/download_script/src/dependency/Pyegi/PythonScripts/%5Bsample%5D%20ColorMania"
    g = github_decode(url)
    g.start()
    # install_script(g)
    # download_script(g)
    # for script in scripts_names:
    #     install_pkgs(script)
    # update_feeds()
