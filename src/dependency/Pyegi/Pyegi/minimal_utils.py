import os
import shutil
import subprocess
import platform
import sys
import re
import appdirs
from enum import Enum
from typing import List
from venv import EnvBuilder
from poetry.core.semver import Version


def normalize_dir_path(dir_path: str) -> str:
    if not dir_path.endswith(("/", "\\")):
        dir_path = dir_path + "/"
    return dir_path


class GlobalPaths:
    def __init__(self, dep_dir: str):
        self.dependency_dir = normalize_dir_path(dep_dir)
        self.pythons_dir = self.dependency_dir + "Pythons/"
        self.installer_dir = self.dependency_dir + "Installer/"
        self.temp_dir = self.pythons_dir + "temp/"
        self.commons_dir = self.pythons_dir + "common-packages/"
        self.scripts_dir = self.dependency_dir + "PythonScripts/"
        self.pyegi_dir = self.dependency_dir + "Pyegi/"
        self.settings_file = self.pyegi_dir + "settings.json"
        self.themes_dir = self.pyegi_dir + "Themes/"


class Platform(Enum):
    UNK = "Unknown"
    MAC = "Darwin"
    LIN = "Linux"
    WIN = "Windows"


def _get_platform() -> Platform:
    platform_name = platform.system()
    if platform_name == Platform.WIN.value:
        return Platform.WIN
    elif platform_name == Platform.LIN.value:
        return Platform.LIN
    elif platform_name == Platform.MAC.value:
        return Platform.MAC
    return Platform.UNK


def _get_aegisub_user_dir():
    path: str
    if PLATFORM == Platform.LIN:
        path = os.path.expanduser("~/.aegisub")
    else:
        path = normalize_dir_path(
            appdirs.user_data_dir(
                "Aegisub",
                "",
                roaming=True,
            )
        )
    return normalize_dir_path(path)


def _get_lib_relative_dir():
    path: str
    if PLATFORM == Platform.WIN:
        path = os.path.join("Lib", "site-packages")
    else:
        path = os.path.join(
            "lib", "python%d.%d" % sys.version_info[:2], "site-packages"
        )
    return normalize_dir_path(path)


def _get_bin_relative_dir():
    path: str
    if PLATFORM == Platform.WIN:
        path = "Scripts"
    else:
        path = "bin"
    return normalize_dir_path(path)


def normalize_binary_path(path: str, is_basename=False) -> str:
    if not is_basename and path.endswith(".exe"):
        path = path[:-4]
    if PLATFORM == Platform.WIN:
        return f"{path}.exe"
    return path


def _get_py_relative_path():
    if PLATFORM == Platform.WIN:
        return normalize_binary_path("python")
    return BIN_RELATIVE_DIR + normalize_binary_path("python3")


class VenvEnvBuilder(EnvBuilder):
    referenced_py_dir_extractor = re.compile(r"home\s=\s(.+)")

    def create_configuration(self, context):
        """
        Create a configuration file indicating where the environment's Python
        was copied from, and whether the system site-packages should be made
        available in the environment.

        :param context: The information for the environment creation request
                        being processed.
        """
        context.cfg_path = path = os.path.join(context.env_dir, "pyvenv.cfg")

        # this part is different from the superclass
        try:
            # we want the correct home python rather than the one from within a potential virtual environment
            with open(
                os.path.join(os.path.dirname(context.python_dir), "pyvenv.cfg"),
                "r",
                encoding="utf-8",
            ) as f:
                context.python_dir = self.referenced_py_dir_extractor.search(
                    f.read().split("\n")[0]
                ).group(1)
        except FileNotFoundError:
            pass  # the rest is the same

        with open(path, "w", encoding="utf-8") as f:
            f.write("home = %s\n" % context.python_dir)
            if self.system_site_packages:
                incl = "true"
            else:
                incl = "false"
            f.write("include-system-site-packages = %s\n" % incl)
            f.write("version = %d.%d.%d\n" % sys.version_info[:3])
            if self.prompt is not None:
                f.write(f"prompt = {self.prompt!r}\n")

    def post_setup(self, context):
        env_lib_path = os.path.join(context.env_dir, LIB_RELATIVE_DIR)
        base_lib_path = os.path.join(context.python_dir, LIB_RELATIVE_DIR).rstrip("/")
        with open(os.path.join(env_lib_path, "pyegi.pth"), "w", encoding="utf-8") as f:
            f.write("%s\n" % base_lib_path)


def run_command(args: List, normalize=False):
    if normalize:
        args[0] = normalize_binary_path(args[0])
    return subprocess.run(args, check=True, capture_output=True)


def rmtree(path: str, exclude: List[str] = []):
    expanded_exclude = set(exclude)
    # expand exclude
    for item in exclude:
        head, _ = os.path.split(item)
        while head:
            expanded_exclude.add(head)
            head, _ = os.path.split(head)
    # remove files respecting exclude
    root_string_len = len(path)
    for parent, dirs, files in os.walk(path):
        head = parent[root_string_len + 1 :]
        while head != "" and head not in exclude:
            head, _ = os.path.split(head)
        if head != "":
            continue
        for name in files:
            target = os.path.join(parent, name)
            target_without_root = target[root_string_len + 1 :]
            if target_without_root not in exclude:
                os.remove(target)
        for name in dirs:
            target = os.path.join(parent, name)
            target_without_root = target[root_string_len + 1 :]
            if target_without_root not in expanded_exclude:
                shutil.rmtree(target, ignore_errors=True)


class PythonVersion:
    def __init__(self, Version):
        self.version = Version
        self.folder_name = f"python{self.version.major}{self.version.minor}"
        self.py_binary_path = os.path.join(
            GLOBAL_PATHS.pythons_dir, self.folder_name, PY_RELATIVE_PATH
        )
        self.common_dir = normalize_dir_path(
            GLOBAL_PATHS.commons_dir + self.folder_name
        )

    def run_module(self, args: List):
        return run_command([self.py_binary_path, "-m"] + args)

    def create_env(self, parent_path, update=False):
        args = [
            self.py_binary_path,
            "-m",
            f"{GLOBAL_PATHS.installer_dir}installer.py",
            "--venv",
            parent_path,
        ]
        if update:
            args.append("--update")
        run_command(args)


PLATFORM = _get_platform()
AEGISUB_USER_DIR = _get_aegisub_user_dir()
LIB_RELATIVE_DIR = _get_lib_relative_dir()
BIN_RELATIVE_DIR = _get_bin_relative_dir()
PY_RELATIVE_PATH = _get_py_relative_path()
GLOBAL_PATHS = GlobalPaths(
    os.path.join(AEGISUB_USER_DIR, "automation", "dependency", "Pyegi/")
)
# the order is important; should be descending
PYTHON_VERSIONS = [
    PythonVersion(Version(3, 10, 5)),
    PythonVersion(Version(3, 9, 13)),
    PythonVersion(Version(3, 8, 13)),
]
