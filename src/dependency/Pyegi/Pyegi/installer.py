import os
from os.path import exists
import sys
import toml
from datetime import datetime as dt1
import shutil
import csv
import json
import warnings


temp_dir = os.path.dirname(__file__) + "/temp/"
commons_dir = os.path.dirname(__file__) + "/commons/"
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
# system_inputs = sys.argv
pyproject_file = "pyproject.toml"
poetry_lock_file = "poetry.lock"
poetry_toml_file = "poetry.toml"


def create_dirs(path):
    parent, _ = os.path.split(path)
    if not exists(parent):
        os.makedirs(parent)


def path_process(path):
    connection_path = "/Lib/site-packages/"
    if path[:3] == "../":
        connection_path = "/Lib/"
        path = path[3:]
        if path[:3] == "../":
            connection_path = "/"
            path = path[3:]
    return path, connection_path


def install_pkg(script):
    print(f"Processing {script} dependencies...")
    script_path = scriptsPath + script + "/"
    if exists(script_path + pyproject_file):
        os.chdir(script_path)
        if exists(script_path + poetry_lock_file):
            os.remove(script_path + poetry_lock_file)
        if exists(script_path + ".venv"):
            shutil.rmtree(script_path + ".venv")
        os.system("poetry lock")
        src = script_path + pyproject_file
        if not exists(temp_dir + poetry_toml_file):
            if not exists(temp_dir):
                os.mkdir(temp_dir)
            toml_file = open(temp_dir + poetry_toml_file, "w")
            toml_file.write("[virtualenvs]\nin-project = true\n")
            toml_file.close()
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
            if package["category"] == "main":
                name_in_commons = f"{package['name']}-{package['version']}"
                f = open(commons_dir + "lib_links.json")
                lib_links = json.load(f)
                f.close()
                is_new_package = True
                for pkg in lib_links["Packages"]:
                    if pkg["Name"] == name_in_commons:
                        if script not in pkg["Scripts"]:
                            pkg["Scripts"].append(script)
                        is_new_package = False
                if is_new_package:
                    lib_link = {}
                    lib_link["Name"] = name_in_commons
                    lib_link["Scripts"] = [script]
                    lib_links["Packages"].append(lib_link)
                json.dump(lib_links, open(commons_dir + "lib_links.json", "w"))
                # check if the package is already in commons
                isdir = os.path.isdir(commons_dir + name_in_commons)
                if isdir:
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
    else:
        print(f'The file "pyproject.toml" doesn\'t exist in {script} script directory.')


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
    for script in scripts_names:
        install_pkg(script)
    # install_pkg("[sample] Disintegration")
