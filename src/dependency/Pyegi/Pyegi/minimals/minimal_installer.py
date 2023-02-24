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
    normal_path_join,
    GLOBAL_PATHS,
    LIB_RELATIVE_DIR,
    ensure_dir_tree,
    rmtree,
)
from typing import List, NamedTuple, Union
from poetry.core.semver import (
    parse_constraint,
    Version,
    VersionRange,
    VersionUnion,
)


class PyInferRes(NamedTuple):
    python_version: PythonVersion
    is_matched: bool


def get_lib_links(lib_links_dir: str):
    lib_links_path = normal_path_join(lib_links_dir, GLOBAL_PATHS.lib_links_filename)
    # initialize if not exist
    if not exists(lib_links_path):
        ensure_dir_tree(lib_links_path)
        lib_links = {"Packages": []}
        with open(lib_links_path, "w") as file:
            json.dump(lib_links, file, indent=4)
    with open(lib_links_path) as file:
        lib_links = json.load(file)
    return lib_links


def clean_lib_links(lib_links_dir):
    lib_links = get_lib_links(lib_links_dir)
    pkgs = []
    for package in lib_links["Packages"]:
        if len(package["Scripts"]) != 0:
            pkgs.append(package)
        else:
            try:
                shutil.rmtree(lib_links_dir + package["Name"])
            except FileNotFoundError:
                pass
    lib_links["Packages"] = pkgs
    with open(lib_links_dir + GLOBAL_PATHS.lib_links_filename, "w") as file:
        json.dump(lib_links, file, indent=4)


def remove_script_from_lib_links(script_id, lib_links_dir):
    lib_links = get_lib_links(lib_links_dir)
    pkgs = []
    for package in lib_links["Packages"]:
        if script_id in package["Scripts"]:
            package["Scripts"].remove(script_id)
        pkgs.append(package)
    lib_links["Packages"] = pkgs
    with open(lib_links_dir + GLOBAL_PATHS.lib_links_filename, "w") as file:
        json.dump(lib_links, file, indent=4)


def add_script_to_lib_links(script_id, pkg_name, lib_links_dir):
    lib_links = get_lib_links(lib_links_dir)
    is_new_package = True
    for pkg in lib_links["Packages"]:
        if pkg["Name"] == pkg_name:
            pkg["Scripts"].append(script_id)
            is_new_package = False
            break
    if is_new_package:
        lib_link = {}
        lib_link["Name"] = pkg_name
        lib_link["Scripts"] = [script_id]
        lib_links["Packages"].append(lib_link)
    with open(lib_links_dir + GLOBAL_PATHS.lib_links_filename, "w") as file:
        json.dump(lib_links, file, indent=4)


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


# copy package from src to common_dir if is_new and create links for targets
def commonize_pkg(
    common_dir: str,
    pkg_name: str,
    targets: List[str],
    src: str = None,
    is_new: bool = False,
):
    if not is_new:
        src = common_dir
    if src == None:
        raise Exception("src is not provided!")

    # create record path
    record_relative_path = normal_path_join(
        LIB_RELATIVE_DIR, f"{pkg_name}.dist-info", "RECORD"
    )
    if is_new:
        record_file_path = normal_path_join(src, ".venv", record_relative_path)
        if not exists(record_file_path):
            raise FileNotFoundError(f"Package {pkg_name} didn't have any RECORD file!")
    else:
        record_file_path = normal_path_join(src, pkg_name, record_relative_path)

    with open(record_file_path, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            relative_path = row[0]
            # normalize relative path
            connection_path, _ = os.path.split(LIB_RELATIVE_DIR)
            while relative_path[:3] == "../":
                # get parent relative path
                connection_path, _ = os.path.split(connection_path)
                # skip ../
                relative_path = relative_path[3:]
            relative_path = normal_path_join(connection_path, relative_path)
            # move if is_new
            path_in_common = f"{common_dir}{pkg_name}/{relative_path}"
            if is_new:
                org_file = f"{src}.venv/{relative_path}"
                ensure_dir_tree(path_in_common)
                if org_file.lower() == record_file_path.lower():
                    shutil.copy(org_file, path_in_common)
                else:
                    shutil.move(org_file, path_in_common)
            # create link
            for target in targets:
                dst = f"{target}.venv/{relative_path}"
                ensure_dir_tree(dst)
                os.link(path_in_common, dst)


def _initialize_script_dir(dir):
    poetry_toml_path = dir + GLOBAL_PATHS.poetry_toml_filename
    if not exists(poetry_toml_path):
        ensure_dir_tree(poetry_toml_path)
        toml_file = open(poetry_toml_path, "w")
        toml_file.write("[virtualenvs]\nin-project = true\n")
        toml_file.close()


def clean_script_folder(
    script_id, keep_files, script_path=None, is_feed=True
) -> Union[PythonVersion, None]:
    if not script_path:
        if is_feed:
            from utils import FeedFile

            feed_file = FeedFile()
            script = feed_file.get_script(script_id)
            script_path = script.folder
            if not script_path:
                return
        else:
            raise ValueError("script_path not provided!")

    print(f"Cleaning {script_id}'s directory...")
    py_version = None
    try:
        # infer python
        py_version = infer_python_version(
            script_path + GLOBAL_PATHS.pyproject_filename
        ).python_version
        com_dir = py_version.common_dir
        # remove from lib_links
        remove_script_from_lib_links(script_id, com_dir)
    except FileNotFoundError:
        pass
    # delete old files
    rmtree(script_path, keep_files)

    if is_feed:
        from utils import FeedFile, InstallationStatus

        feed_file = FeedFile()
        script = feed_file.get_script(script_id)
        script.installed_version = ""
        script.installed_version_description = ""
        script.installation_status = InstallationStatus.CLEANED
        feed_file.update_script(script)

    return py_version


def install_pkgs(script_id, script_path=None, is_feed=True) -> PythonVersion:
    if is_feed and not script_path:
        from utils import FeedFile

        feed_file = FeedFile()
        script = feed_file.get_script(script_id)
        script_path = script.folder
    if not script_path:
        raise ValueError("script_path is unknown!")

    print(f"Processing {script_id} dependencies...")
    # create poetry.toml
    _initialize_script_dir(GLOBAL_PATHS.temp_dir)
    _initialize_script_dir(script_path)
    # infer python
    py_version = infer_python_version(
        script_path + GLOBAL_PATHS.pyproject_filename
    ).python_version
    com_dir = py_version.common_dir
    # renew venvs
    py_version.create_env(script_path)
    py_version.create_env(GLOBAL_PATHS.temp_dir)

    # start installing process
    # create lock file
    old_cwd = os.getcwd()
    os.chdir(script_path)
    result = py_version.run_module(["poetry", "lock"])
    print(result.stdout)
    # copy pyproject and lock file to temp
    src = script_path + GLOBAL_PATHS.pyproject_filename
    dst = GLOBAL_PATHS.temp_dir + GLOBAL_PATHS.pyproject_filename
    shutil.copyfile(src, dst)
    src = script_path + GLOBAL_PATHS.poetry_lock_filename
    dst = GLOBAL_PATHS.temp_dir + GLOBAL_PATHS.poetry_lock_filename
    shutil.copyfile(src, dst)
    # analyse lock file
    lock_content = toml.load(script_path + GLOBAL_PATHS.poetry_lock_filename)
    packages = lock_content["package"]
    new_packages = []
    for package in packages:
        if package["category"] != "main":
            continue
        name_in_commons = f"{package['name']}-{package['version']}"
        # update lib_links
        add_script_to_lib_links(script_id, name_in_commons, com_dir)
        # check if the package is already in commons
        dir_exist = os.path.isdir(com_dir + name_in_commons)
        if dir_exist:
            # create links for existing packages
            commonize_pkg(
                com_dir, name_in_commons, [GLOBAL_PATHS.temp_dir, script_path]
            )
        else:
            new_packages.append(name_in_commons)
    # install new packages
    os.chdir(GLOBAL_PATHS.temp_dir)
    result = py_version.run_module(["poetry", "install", "--no-dev", "--no-root"])
    print(result.stdout)
    # update common-packages and create links
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
    os.chdir(old_cwd)

    # removing temp dir
    shutil.rmtree(GLOBAL_PATHS.temp_dir)
    # remove unused packages from commons
    clean_lib_links(com_dir)

    # update feed file
    if is_feed:
        from utils import FeedFile, InstallationStatus

        feed_file = FeedFile()
        script = feed_file.get_script(script_id)
        script.installation_status = InstallationStatus.COMPLETED
        feed_file.update_script(script)

    return py_version
