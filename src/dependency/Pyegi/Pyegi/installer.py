import os
from os.path import exists
import sys
import toml
from datetime import datetime as dt1
import shutil
import csv
import json

start_time = dt1.now()
print("\nStart time: " + str(start_time) + "\n")

temp_dir = os.path.dirname(__file__) + "/temp/"
commons_dir = os.path.dirname(__file__) + "/commons/"
dependency_dir = os.path.dirname(os.path.dirname(__file__)) + "/"
scriptsPath = dependency_dir + "PythonScripts/"
# system_inputs = sys.argv

scripts_names = [
    name
    for name in os.listdir(scriptsPath)
    if os.path.isdir(os.path.join(scriptsPath, name))
]


def create_dirs(path):
    parent, _ = os.path.split(path)
    if not exists(parent):
        os.makedirs(parent)


def install_pkg(script):
    print(f"Processing {script} dependencies...")
    script_path = scriptsPath + script + "/"
    if exists(script_path + "pyproject.toml"):
        os.chdir(script_path)
        os.system("poetry lock")
        src = script_path + "pyproject.toml"
        dst = temp_dir + "pyproject.toml"
        shutil.copyfile(src, dst)
        os.chdir(temp_dir)
        os.system("poetry lock")
        lock_content = toml.load("poetry.lock")
        packages = lock_content["package"]
        packages_to_move = []
        phase1_start_time = dt1.now()
        for package in packages:
            name_in_commons = f"{package['name']}-{package['version']}"
            f = open(commons_dir + "lib_links.json")
            lib_links = json.load(f)
            f.close()
            new_package = True
            for pkg in lib_links["Packages"]:
                if pkg["name"] == name_in_commons:
                    if script not in pkg["scripts"]:
                        pkg["scripts"].append(script)
                    new_package = False
            if new_package:
                lib_link = {}
                lib_link["name"] = name_in_commons
                lib_link["scripts"] = [script]
                lib_links["Packages"].append(lib_link)
            json.dump(lib_links, open(commons_dir + "lib_links.json", "w"))
            isdir = os.path.isdir(commons_dir + name_in_commons)
            if isdir:
                filename = f"{commons_dir + name_in_commons}/Lib/site-packages/{name_in_commons}.dist-info/RECORD"
                paths = []
                with open(filename, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        paths.append(row[0])
                for path in paths:
                    connection_path = "/Lib/site-packages/"
                    if path[:3] == "../":
                        connection_path = "/Lib/"
                        path = path[3:]
                        if path[:3] == "../":
                            connection_path = "/"
                            path = path[3:]
                    src = commons_dir + name_in_commons + connection_path + path
                    dst = f"{temp_dir}.venv{connection_path + path}"
                    create_dirs(dst)
                    os.symlink(src, dst)
                    dst = f"{script_path}.venv{connection_path + path}"
                    create_dirs(dst)
                    os.symlink(src, dst)
            else:
                packages_to_move.append(name_in_commons)
        phase1_end_time = dt1.now()
        print("Total phase 1 time: " + str(phase1_end_time - phase1_start_time))

        os.system("poetry install")
        phase2_start_time = dt1.now()
        for name_in_commons in packages_to_move:
            filename = (
                f"{temp_dir}.venv/Lib/site-packages/{name_in_commons}.dist-info/RECORD"
            )
            if exists(filename):
                paths = []
                with open(filename, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        paths.append(row[0])
                for path in paths:
                    connection_path = "/Lib/site-packages/"
                    if path[:3] == "../":
                        connection_path = "/Lib/"
                        path = path[3:]
                        if path[:3] == "../":
                            connection_path = "/"
                            path = path[3:]
                    src = f"{temp_dir}.venv{connection_path + path}"
                    dst = commons_dir + name_in_commons + connection_path + path
                    create_dirs(dst)
                    shutil.move(src, dst)
                    dst2 = f"{script_path}.venv{connection_path + path}"
                    create_dirs(dst2)
                    os.symlink(dst, dst2)
        phase2_end_time = dt1.now()
        print("Total phase 2 time: " + str(phase2_end_time - phase2_start_time))
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(temp_dir)
        os.mkdir("temp")
        toml_file = open(temp_dir + "poetry.toml", "w")
        toml_file.write("[virtualenvs]\nin-project = true")
        toml_file.close()
    else:
        print(f'The file "pyproject.toml" doesn\'t exist in {script} script directory.')


def clean_lib_links(script):
    f = open(commons_dir + "lib_links.json")
    lib_links = json.load(f)
    f.close()
    pkgs = []
    zero_pkgs = []
    for package in lib_links["Packages"]:
        if script in package["scripts"]:
            package["scripts"].remove(script)
            if len(package["scripts"]) == 0:
                if exists(commons_dir + package["name"]):
                    zero_pkgs.append(package["name"])
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


for script in scripts_names:
    install_pkg(script)

# install_pkg("[sample] Disintegration")


end_time = dt1.now()
print("\n\nEnd time: " + str(end_time) + "\n")
print("Total run time: " + str(end_time - start_time))
