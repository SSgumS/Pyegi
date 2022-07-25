import logging
import os
import shutil
import appdirs

logger = logging.getLogger(__name__)


def run_step(context: dict):
    automation_path = os.path.join(
        appdirs.user_data_dir("Aegisub", "", roaming=True), "automation"
    )
    pyegi_dependency_path = os.path.join(automation_path, "dependency", "Pyegi")

    # Remove previous files
    shutil.rmtree(os.path.join(automation_path, "include", "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_dependency_path, ".venv"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_dependency_path, "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_dependency_path, "PythonScripts"), ignore_errors=True)

    # Copy new files
    shutil.copytree("src", automation_path, dirs_exist_ok=True)
    shutil.copy("poetry.toml", pyegi_dependency_path)
    shutil.copy("pyproject.toml", pyegi_dependency_path)
