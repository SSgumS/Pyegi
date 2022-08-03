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


temp_dir = os.path.dirname(__file__) + "/temp/"
commons_dir = os.path.dirname(__file__) + "/commons/"
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
# system_inputs = sys.argv
pyproject_file = "pyproject.toml"
poetry_lock_file = "poetry.lock"
poetry_toml_file = "poetry.toml"


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


def download_script(url):
    g = github_decode(url)

    files, folders = g.get_files_and_folders()

    script_path = scriptsPath + g.script_name + "/"
    for folder in folders:
        path = script_path + folder
        if not exists(path):
            os.makedirs(path)

    if not exists(script_path):
        os.makedirs(script_path)

    for file in files:
        file_download_url = g.get_download_url(file, g.prefix)
        file_name = f"{script_path}{file}"
        urllib.request.urlretrieve(file_download_url, file_name)


def install_pkg(script):
    print(f"Processing {script} dependencies...")
    script_path = scriptsPath + script + "/"
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
        os.system("poetry lock")
        src = script_path + pyproject_file
        dst = temp_dir + pyproject_file
        shutil.copyfile(src, dst)
        src = script_path + poetry_lock_file
        dst = temp_dir + poetry_lock_file
        shutil.copyfile(src, dst)
        os.chdir(temp_dir)
        os.system("poetry lock --no-update")
        lock_content = toml.load(poetry_lock_file)
        packages = lock_content["package"]
        new_packages = []
        for package in packages:
            if package["category"] != "main":
                continue
            name_in_commons = f"{package['name']}-{package['version']}"
            try:
                zero_pkgs.remove(name_in_commons)
            except ValueError:
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
                        os.symlink(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        create_dirs(dst)
                        os.symlink(src, dst)
            else:
                new_packages.append(name_in_commons)

        os.system("poetry install --no-dev")
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
                        shutil.move(src, dst)
                        dst2 = f"{script_path}.venv{connection_path + path}"
                        create_dirs(dst2)
                        os.symlink(dst, dst2)
            else:
                warnings.warn(f"Package {name_in_commons} didn't have any RECORD file.")
        os.chdir(os.path.dirname(__file__))
        # removing temp dir
        shutil.rmtree(temp_dir)
        # remove unused packages from commons
        for zero_pkg in zero_pkgs:
            shutil.rmtree(commons_dir + zero_pkg)
    else:
        print(f'The file "pyproject.toml" doesn\'t exist in {script} script directory.')


def uninstall_pkg(script):
    print(f"Processing {script} dependencies...")
    script_path = scriptsPath + script + "/"
    shutil.rmtree(script_path)
    zero_pkgs = clean_lib_links(script)
    for zero_pkg in zero_pkgs:
        shutil.rmtree(commons_dir + zero_pkg)


if __name__ == "__main__":
    scripts_names = [
        name
        for name in os.listdir(scriptsPath)
        if os.path.isdir(os.path.join(scriptsPath, name))
    ]
    # url = "https://github.com/SSgumS/Pyegi/tree/main/src/dependency/Pyegi/PythonScripts/%5Bsample%5D%20ColorMania"
    # url = "https://github.com/SSgumS/Pyegi/tree/main/src/dependency/Pyegi/PythonScripts/%5Bsample%5D%20Disintegration"
    # url = "https://github.com/SSgumS/Pyegi/tree/load_script_details"
    # url = "https://github.com/python-poetry/poetry-core/tree/1.1.0a6"
    # url = "https://github.com/mzn928/Aegisub_Persian-Toolkit"
    url = "https://github.com/python-poetry/poetry-core"
    # url = "https://github.com/TypesettingTools/DependencyControl"
    download_script(url)
    # for script in scripts_names:
    #     install_pkg(script)
    # install_pkg("[sample] Disintegration")
