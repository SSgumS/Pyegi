import argparse
import os
import sys
import shutil

sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))
sys.argv.append("--use-global-dependency-path")

from Pyegi.minimals.minimal_utils import (
    rmtree,
    cptree,
    normal_path_join,
    AEGISUB_USER_DIR,
    VenvEnvBuilder,
    GLOBAL_PATHS,
)
from Pyegi.minimals.minimal_pkg_installer import (
    install_pkgs,
    clean_script_folder,
    clean_lib_links,
)


def _create_env(parent_path, update=False):
    builder = VenvEnvBuilder(clear=(not update), upgrade=update, with_pip=True)
    builder.create(normal_path_join(parent_path, ".venv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # install args
    parser.add_argument("--install", action="store_true", help="Install Pyegi")
    parser.add_argument("--update-pythons", action="store_true", help="Update Pythons")
    # venv args
    parser.add_argument("--venv", type=str, help="Create a venv")
    parser.add_argument("--update", action="store_true", help="Update venv")
    args, _ = parser.parse_known_args()

    if args.install:
        # go to base folder of project
        current_dir = os.path.dirname(__file__)
        while True:
            parent_dir = os.path.dirname(current_dir)
            if os.path.basename(current_dir) == "src":
                break
            elif current_dir == parent_dir:
                raise FileNotFoundError("Couldn't find the base folder of the project.")
            else:
                current_dir = parent_dir
        os.chdir(parent_dir)
        automation_path = normal_path_join(AEGISUB_USER_DIR, "automation", is_dir=True)
        dependency_dir = normal_path_join(
            automation_path, "dependency", "Pyegi", is_dir=True
        )
        pyegi_dir = normal_path_join(dependency_dir, "Pyegi", is_dir=True)
        script_id = "SSgumS/Pyegi/"
        # remove previous files
        print("Removing previous files...")
        # include
        shutil.rmtree(
            normal_path_join(automation_path, "include", "Pyegi", is_dir=True),
            ignore_errors=True,
        )
        # dependency
        excludes = ["Pyegi/", "PythonScripts/"]
        if args.update_pythons:
            excludes.append("Pythons/common-packages/")
        else:
            excludes.append("Pythons/")
        rmtree(dependency_dir, excludes)
        # pyegi
        try:
            os.remove(normal_path_join(pyegi_dir, "Themes", "Pyegi.css"))
        except FileNotFoundError:
            pass
        excludes = ["settings.json", "scripts_feed.json", "Themes/"]
        old_py_version = clean_script_folder(
            script_id, excludes, script_path=pyegi_dir, is_feed=False
        )
        # copy new files
        print("Copying new files...")
        # NOTICE: scripts' binaries are broken because of the static linking
        cptree(
            "src/", automation_path, excludes=["dependency/Pyegi/Pyegi/settings.json"]
        )
        shutil.copy2(GLOBAL_PATHS.poetry_toml_filename, pyegi_dir)
        shutil.copy2(GLOBAL_PATHS.pyproject_filename, pyegi_dir)
        # install Pyegi dependencies
        new_py_version = install_pkgs(script_id, script_path=pyegi_dir, is_feed=False)
        # cleanup old python's commons
        if old_py_version != new_py_version and old_py_version:
            clean_lib_links(old_py_version.common_dir)

        print("Pyegi has been installed successfully!")
    elif args.venv != None:
        if len(args.venv) == 0:
            raise ValueError("You didn't provide any path for venv's parent!")
        _create_env(args.venv, args.update)
