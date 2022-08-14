import os
import toml
import shutil
from minimals.minimal_installer import *
from utils import (
    normalize_path,
    normal_path_join,
    GLOBAL_PATHS,
)


def ensure_init_file(script_path):
    init_path = normal_path_join(script_path, "__init__.py")
    code_section = (
        "import os\n"
        "import sys\n"
        "import pathlib\n"
        "file = pathlib.Path(__file__).resolve()\n"
        'sys.path.append(os.path.join(str(file.parents[2]), "Pyegi"))\n'
    )
    if os.path.exists(init_path):
        # insert the code section at the beginning
        with open(init_path, "r") as f:
            lines = f.readlines()
        with open(init_path, "w") as f:
            f.write(code_section)
            for line in lines:
                f.write(line)
    else:
        with open(init_path, "w") as f:
            f.write(code_section)


def uninstall_script(script_path):
    # normalize dir path
    script_path = normalize_path(script_path, True)
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
        if os.path.isdir(normal_path_join(GLOBAL_PATHS.scripts_dir, name))
    ]
    for script in scripts_names:
        install_pkgs(script)
    # install_pkgs("[sample] Disintegration")
