import logging
import os
import shutil
import appdirs

logger = logging.getLogger(__name__)


def run_step(context: dict):
    automation_path = os.path.join(
        appdirs.user_data_dir("Aegisub", "", roaming=True), "automation"
    )
    pyegi_config_path = os.path.join(automation_path, "config", "Pyegi")

    # Remove previous files
    shutil.rmtree(os.path.join(automation_path, "include", "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_config_path, ".venv"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_config_path, "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(pyegi_config_path, "PythonScripts"), ignore_errors=True)

    # Copy new files
    shutil.copytree("src", automation_path, dirs_exist_ok=True)
    shutil.copytree(
        ".venv", os.path.join(pyegi_config_path, ".venv"), dirs_exist_ok=True
    )
    shutil.copy("poetry.toml", pyegi_config_path)
    shutil.copy("pyproject.toml", pyegi_config_path)
