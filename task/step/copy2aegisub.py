import logging
import os
import shutil
import appdirs

logger = logging.getLogger(__name__)

def run_step(context: dict):
    automation_path = os.path.join(appdirs.user_data_dir("Aegisub", "", roaming=True), "automation")

    # Remove previous files
    shutil.rmtree(os.path.join(automation_path, "include", "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(automation_path, "config", "Pyegi", "Pyegi"), ignore_errors=True)
    shutil.rmtree(os.path.join(automation_path, "config", "Pyegi", "PythonScripts"), ignore_errors=True)

    # Copy new files
    src_path = "src"
    target_path = automation_path
    shutil.copytree(src_path, target_path, dirs_exist_ok=True)
