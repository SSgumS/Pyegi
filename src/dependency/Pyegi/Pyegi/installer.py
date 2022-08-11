import os
from os.path import exists
import toml
import shutil
import warnings
from minimal_installer import *
from utils import (
    normalize_dir_path,
    GLOBAL_PATHS,
)


def _initialize_script_dir(dir):
    poetry_toml_path = dir + poetry_toml_file
    if not exists(poetry_toml_path):
        ensure_dir_tree(poetry_toml_path)
        toml_file = open(poetry_toml_path, "w")
        toml_file.write("[virtualenvs]\nin-project = true\n")
        toml_file.close()


def install_pkgs(script_path):
    print(f"Processing {script_path} dependencies...")
    # normalize dir path
    script_path = normalize_dir_path(script_path)
    # create poetry.toml
    _initialize_script_dir(GLOBAL_PATHS.temp_dir)
    _initialize_script_dir(script_path)
    # infer python
    py_version = infer_python_version(script_path + pyproject_file).python_version
    com_dir = py_version.common_dir
    # removing script from lib_links
    zero_pkgs = clean_lib_links(script_path, com_dir)
    # renew venvs
    py_version.create_env(script_path)
    py_version.create_env(GLOBAL_PATHS.temp_dir)
    # start installing process
    # create lock file
    os.chdir(script_path)
    py_version.run_module(["poetry", "lock"])
    # copy pyproject and lock file to temp
    src = script_path + pyproject_file
    dst = GLOBAL_PATHS.temp_dir + pyproject_file
    shutil.copyfile(src, dst)
    src = script_path + poetry_lock_file
    dst = GLOBAL_PATHS.temp_dir + poetry_lock_file
    shutil.copyfile(src, dst)
    # analyse lock file
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
        update_lib_links(script_path, name_in_commons, com_dir)
        # check if the package is already in commons
        dir_exist = os.path.isdir(com_dir + name_in_commons)
        if dir_exist:
            # create symlinks for existing packages
            commonize_pkg(
                com_dir, name_in_commons, [GLOBAL_PATHS.temp_dir, script_path]
            )
        else:
            new_packages.append(name_in_commons)
    # install new packages
    os.chdir(GLOBAL_PATHS.temp_dir)
    py_version.run_module(["poetry", "install", "--no-dev"])
    # update common-packages and create symlinks
    for name_in_commons in new_packages:
        try:
            commonize_pkg(
                com_dir,
                name_in_commons,
                [script_path],
                src=GLOBAL_PATHS.temp_dir,
                is_new=True,
            )
        except FileNotFoundError as e:
            warnings.warn(e)
    # revert current location
    os.chdir(os.path.dirname(__file__))
    # removing temp dir
    shutil.rmtree(GLOBAL_PATHS.temp_dir)
    # remove unused packages from commons
    for zero_pkg in zero_pkgs:
        shutil.rmtree(com_dir + zero_pkg)


def uninstall_script(script_path):
    # normalize dir path
    script_path = normalize_dir_path(script_path)
    # infer python
    pyproject_file_path = script_path + pyproject_file
    py_result = infer_python_version(toml.load(pyproject_file_path))
    # remove dirs
    shutil.rmtree(script_path)
    # clean common-packages
    com_dir = GLOBAL_PATHS.commons_dir + py_result.python_version.folder_name + "/"
    zero_pkgs = clean_lib_links(script_path, com_dir)
    for zero_pkg in zero_pkgs:
        shutil.rmtree(com_dir + zero_pkg)


if __name__ == "__main__":
    scripts_names = [
        name
        for name in os.listdir(GLOBAL_PATHS.scripts_dir)
        if os.path.isdir(os.path.join(GLOBAL_PATHS.scripts_dir, name))
    ]
    for script in scripts_names:
        install_pkgs(script)
    # install_pkgs("[sample] Disintegration")
