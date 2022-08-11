import argparse
import os
import shutil
from ..Pyegi.minimal_utils import (
    rmtree,
    AEGISUB_USER_DIR,
    VenvEnvBuilder,
)
from ..Pyegi.minimal_installer import (
    commonize_venv,
    infer_python_version,
    pyproject_file,
    poetry_toml_file,
)


def _create_env(parent_path, update=False):
    builder = VenvEnvBuilder(
        clear=(not update), symlinks=True, upgrade=update, with_pip=True
    )
    builder.create(os.path.join(parent_path, ".venv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--venv", type=str)
    parser.add_argument("--update", action="store_true")
    args, unknown_args = parser.parse_known_args()

    if args.install:
        # renew files
        os.chdir("../../../../")  # go to base folder of project
        automation_path = os.path.join(
            AEGISUB_USER_DIR,
            "automation/",
        )
        dependency_dir = os.path.join(automation_path, "dependency", "Pyegi/")
        pyegi_dir = os.path.join(dependency_dir, "Pyegi/")
        # remove previous files
        shutil.rmtree(
            os.path.join(automation_path, "include", "Pyegi"), ignore_errors=True
        )
        rmtree(dependency_dir, ["Pyegi/settings.json", "Pythons/common-packages"])
        # copy new files
        shutil.copytree("src", automation_path, dirs_exist_ok=True)
        shutil.copy(poetry_toml_file, pyegi_dir)
        shutil.copy(pyproject_file, pyegi_dir)

        # install Pyegi dependencies
        os.chdir(pyegi_dir)
        py_version = infer_python_version(pyegi_dir + pyproject_file).python_version
        py_version.create_env(pyegi_dir)
        # NOTICE: scripts' binaries are broken because of the static linking
        py_version.run_module(["poetry", "install", "--no-dev"])
        commonize_venv(pyegi_dir)
    elif args.venv != None:
        if len(args.venv) == 0:
            raise ValueError("You didn't provide any path for venv's parent!")
        _create_env(args.venv, args.update)
