from genericpath import exists
import logging
import os
import shutil
import appdirs
import time
from typing import Union

logger = logging.getLogger(__name__)


def get_last_modified(path: str, in_float: bool = False) -> Union[str, float]:
    last_modified = max(os.path.getmtime(root) for root, _, _ in os.walk(path))
    if in_float:
        return last_modified
    else:
        return time.ctime(last_modified)


def run_step(context: dict):
    automation_path = os.path.join(
        appdirs.user_data_dir("Aegisub", "", roaming=True), "automation"
    )
    pyegi_dependency_path = os.path.join(automation_path, "dependency", "Pyegi")

    # Remove previous files
    shutil.rmtree(os.path.join(automation_path, "include", "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_dependency_path, "Pyegi"), ignore_errors=True)
    shutil.rmtree(
        os.path.join(pyegi_dependency_path, "PythonScripts"), ignore_errors=True
    )

    # Copy new files
    os.makedirs(os.path.join(pyegi_dependency_path, "PythonScripts"))
    shutil.copytree(
        "src/dependency/Pyegi/PythonScripts/[sample] prefix",
        os.path.join(pyegi_dependency_path, "PythonScripts", "[sample] prefix"),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        "src/dependency/Pyegi/Pyegi",
        os.path.join(pyegi_dependency_path, "Pyegi"),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        "src/include",
        os.path.join(automation_path, "include"),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        "src/autoload",
        os.path.join(automation_path, "autoload"),
        dirs_exist_ok=True,
    )
    shutil.copy("poetry.toml", pyegi_dependency_path)
    shutil.copy("pyproject.toml", pyegi_dependency_path)

    # Copy .venv
    target_venv_path = os.path.join(pyegi_dependency_path, ".venv")
    if not exists(target_venv_path):
        os.symlink(os.path.abspath(".venv"), target_venv_path, target_is_directory=True)
