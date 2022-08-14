import os
from os.path import exists
import shutil
import csv
import toml
import json
import warnings
from .minimal_utils import (
    PYTHON_VERSIONS,
    PythonVersion,
    normalize_path,
    normal_path_join,
    GLOBAL_PATHS,
    LIB_RELATIVE_DIR,
)
from typing import List, NamedTuple
from poetry.core.semver import (
    parse_constraint,
    Version,
    VersionRange,
    VersionUnion,
)


pyproject_file = "pyproject.toml"
poetry_toml_file = "poetry.toml"
poetry_lock_file = "poetry.lock"
lib_links_file = "lib_links.json"


class PyInferRes(NamedTuple):
    python_version: PythonVersion
    is_matched: bool


def ensure_dir_tree(path):
    parent, _ = os.path.split(path)
    if not exists(parent):
        os.makedirs(parent)


def get_lib_links(lib_links_path: str):
    # initialize if not exist
    if not exists(lib_links_path):
        ensure_dir_tree(lib_links_path)
        lib_links = {"Packages": []}
        with open(lib_links_path, "w") as file:
            json.dump(lib_links, file)
    with open(lib_links_path) as file:
        lib_links = json.load(file)
    return lib_links


def clean_lib_links(script, lib_links_dir):
    lib_links_path = normal_path_join(lib_links_dir, lib_links_file)
    lib_links = get_lib_links(lib_links_path)
    pkgs = []
    zero_pkgs = []
    for package in lib_links["Packages"]:
        if script in package["Scripts"]:
            package["Scripts"].remove(script)
            if len(package["Scripts"]) == 0:
                if exists(lib_links_dir + package["Name"]):
                    zero_pkgs.append(package["Name"])
            else:
                pkgs.append(package)
        else:
            pkgs.append(package)
    lib_links["Packages"] = pkgs
    with open(lib_links_path, "w") as file:
        json.dump(lib_links, file)
    return zero_pkgs


def update_lib_links(script, pkg_name, lib_links_dir):
    lib_links_path = normal_path_join(lib_links_dir, lib_links_file)
    lib_links = get_lib_links(lib_links_path)
    is_new_package = True
    for pkg in lib_links["Packages"]:
        if pkg["Name"] == pkg_name:
            pkg["Scripts"].append(script)
            is_new_package = False
            break
    if is_new_package:
        lib_link = {}
        lib_link["Name"] = pkg_name
        lib_link["Scripts"] = [script]
        lib_links["Packages"].append(lib_link)
    with open(lib_links_path, "w") as file:
        json.dump(lib_links, file)


def _check_approximation_for_version_range(range: VersionRange, target: Version):
    max = range.max
    if range.include_max:
        if max.major == target.major and max.minor == target.minor:
            return True
    elif max.major == target.major and (max.minor - 1) == target.minor:
        min = range.min
        if (max.minor - 1) >= min.minor:
            return True
    return False


def infer_python_version(pyproject_path: str) -> PyInferRes:
    pyproject = toml.load(pyproject_path)
    version_constraint_str = pyproject["tool"]["poetry"]["dependencies"]["python"]
    version_constraint = parse_constraint(version_constraint_str)
    for py_version in PYTHON_VERSIONS:
        version = py_version.version
        if version_constraint.allows(version):
            return PyInferRes(py_version, True)
    # not matched cases
    result = None
    for py_version in PYTHON_VERSIONS:
        version = py_version.version
        if version_constraint.is_empty():
            result = PyInferRes(PYTHON_VERSIONS[0], False)
        elif (
            isinstance(version_constraint, Version)
            and version_constraint.major == version.major
            and version_constraint.minor == version.minor
        ):
            result = PyInferRes(py_version, False)
        elif isinstance(version_constraint, VersionRange):
            if _check_approximation_for_version_range(version_constraint, version):
                result = PyInferRes(py_version, False)
        elif isinstance(version_constraint, VersionUnion):
            for range in version_constraint.ranges:
                if _check_approximation_for_version_range(range, version):
                    result = PyInferRes(py_version, False)
    if result == None:
        result = PyInferRes(PYTHON_VERSIONS[0], False)
    warnings.warn(
        f"No python version matched. Choosed {result.python_version.version}, the nearest or the newest one."
    )
    return result


def commonize_pkg(
    common_dir: str,
    pkg_name: str,
    targets: List[str],
    src: str = None,
    is_new: bool = False,
):
    if not is_new:
        src = common_dir
    elif src not in targets:
        targets.append(src)
    if src == None:
        raise Exception("src is not provided!")
    file_path = normal_path_join(
        src, pkg_name, LIB_RELATIVE_DIR, f"{pkg_name}.dist-info", "RECORD"
    )
    if is_new and not exists(file_path):
        raise FileNotFoundError(f"Package {pkg_name} didn't have any RECORD file!")
    with open(file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            relative_path = row[0]
            # normalize relative path
            connection_path, _ = os.path.split(LIB_RELATIVE_DIR)
            while relative_path[:3] == "../":
                connection_path, _ = os.path.split(connection_path)
                relative_path = relative_path[3:]
            relative_path = normal_path_join(connection_path, relative_path)
            # move if necessary
            path_in_common = f"{common_dir}{pkg_name}/{relative_path}"
            if is_new:
                org_file = f"{src}.venv/{relative_path}"
                ensure_dir_tree(path_in_common)
                shutil.move(org_file, path_in_common)
            # create link
            for target in targets:
                dst = f"{target}.venv/{relative_path}"
                ensure_dir_tree(dst)
                os.link(path_in_common, dst)


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
    script_path = normalize_path(script_path, True)
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
