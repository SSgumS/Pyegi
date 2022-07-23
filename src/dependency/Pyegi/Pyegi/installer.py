import os
from os.path import exists
import sys
import toml
from datetime import datetime as dt1
import shutil
import csv

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


def install_pkgs(script):
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
        for package in packages:
            name_in_commons = f"{package['name']}-{package['version']}"
            isdir = os.path.isdir(commons_dir + name_in_commons)
            site_packages_dirs = []
            if isdir:
                filename = f"{commons_dir + name_in_commons}/Lib/site-packages/{name_in_commons}.dist-info/RECORD"
                paths = []
                with open(filename, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        paths.append(row[0])
                for path in paths:
                    if path[:3] == "../":
                        connection_path = "/Lib/"
                        path = path[3:]
                        if path[:3] == "../":
                            connection_path = "/"
                            path = path[3:]
                        src = commons_dir + name_in_commons + connection_path + path
                        dst = f"{temp_dir}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(src, dst)
                    elif path[:12] == "__pycache__/":
                        connection_path = "/Lib/site-packages/"
                        src = commons_dir + name_in_commons + connection_path + path
                        dst = f"{temp_dir}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(src, dst)
                    elif "/" in path:
                        while True:
                            parent = path
                            path, _ = os.path.split(path)
                            if path == "":
                                break
                        connection_path = "/Lib/site-packages/"
                        if parent not in site_packages_dirs:
                            site_packages_dirs.append(parent)
                            src = (
                                commons_dir + name_in_commons + connection_path + parent
                            )
                            dst = f"{temp_dir}.venv{connection_path + parent}"
                            os.symlink(src, dst)
                            dst = f"{script_path}.venv{connection_path + parent}"
                            os.symlink(src, dst)
                    else:
                        connection_path = "/Lib/site-packages/"
                        src = commons_dir + name_in_commons + connection_path + path
                        dst = f"{temp_dir}.venv{connection_path + path}"
                        os.symlink(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        os.symlink(src, dst)
            else:
                packages_to_move.append(name_in_commons)

        os.system("poetry install")
        for name_in_commons in packages_to_move:
            site_packages_dirs = []
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
                    if path[:3] == "../":
                        connection_path = "/Lib/"
                        path = path[3:]
                        if path[:3] == "../":
                            connection_path = "/"
                            path = path[3:]
                        src = f"{temp_dir}.venv{connection_path + path}"
                        dst = commons_dir + name_in_commons + connection_path + path
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        shutil.move(src, dst)
                        dst2 = f"{script_path}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst2)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(dst, dst2)
                    elif path[:12] == "__pycache__/":
                        connection_path = "/Lib/site-packages/"
                        src = f"{temp_dir}.venv{connection_path + path}"
                        dst = commons_dir + name_in_commons + connection_path + path
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        shutil.move(src, dst)
                        dst = f"{script_path}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        dst2 = f"{script_path}.venv{connection_path + path}"
                        path2, _ = os.path.split(dst2)
                        if not exists(path2):
                            os.makedirs(path2)
                        os.symlink(dst, dst2)
                    elif "/" in path:
                        while True:
                            parent = path
                            path, _ = os.path.split(path)
                            if path == "":
                                break
                        connection_path = "/Lib/site-packages/"
                        if parent not in site_packages_dirs:
                            site_packages_dirs.append(parent)
                            src = f"{temp_dir}.venv{connection_path + parent}"
                            dst = (
                                commons_dir + name_in_commons + connection_path + parent
                            )
                            if not exists(
                                commons_dir + name_in_commons + connection_path
                            ):
                                os.makedirs(
                                    commons_dir + name_in_commons + connection_path
                                )
                            shutil.move(src, dst)
                            dst2 = f"{script_path}.venv{connection_path + parent}"
                            os.symlink(dst, dst2)
                    else:
                        connection_path = "/Lib/site-packages/"
                        src = f"{temp_dir}.venv{connection_path + path}"
                        dst = commons_dir + name_in_commons + connection_path + path
                        path2, _ = os.path.split(dst)
                        if not exists(path2):
                            os.makedirs(path2)
                        shutil.move(src, dst)
                        dst2 = f"{script_path}.venv{connection_path + path}"
                        os.symlink(dst, dst2)
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(temp_dir)
        os.mkdir("temp")
        toml_file = open(temp_dir + "poetry.toml", "w")
        toml_file.write("[virtualenvs]\nin-project = true")
        toml_file.close()
    else:
        print(f'The file "pyproject.toml" doesn\'t exist in {script} script directory.')


"""
for script in scripts_names:
    install_pkgs(script)
"""
install_pkgs("[sample] ColorMania")


end_time = dt1.now()
print("\n\nEnd time: " + str(end_time) + "\n")
print("Total run time: " + str(end_time - start_time))
