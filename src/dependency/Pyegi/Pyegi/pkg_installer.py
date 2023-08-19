import os
import shutil
from typing import List
import numpy as np
import re
from minimals.minimal_pkg_installer import *
from utils import (
    normalize_path,
    normal_path_join,
    GLOBAL_PATHS,
    FeedParser,
    DEVELOPMENT_MODE,
    ScriptPyProject,
    download_file,
    FeedFile,
    InstallationStatus,
)


def add_to_feed(feed: FeedParser, main_known_feeds: List[FeedParser]) -> List[str]:
    if not feed.script_info.discoverable:
        return []

    # prioritize main feeds
    for main_feed in main_known_feeds:
        if feed.ID == main_feed.ID and feed.url != main_feed.url:
            return []
    # prioritize existing feed in a special situation
    feed_file = FeedFile().raw
    feed.populate_relevant_tags()
    if (
        (feed.ID in feed_file)
        and feed_file[feed.ID]["url"] != feed.url
        and (not feed.is_main_branch())
        and (not feed.relevant_tags)
    ):
        date_time = feed.datetime
        local_date_time = FeedParser.parse_datetime(feed_file[feed.ID]["raw_datetime"])
        if feed_file[feed.ID]["is_main_branch"] or local_date_time > date_time:
            try:
                feed = FeedParser(feed_file[feed.ID]["url"])
            except:
                pass

    # update feed file entry
    try:
        folder_name = feed_file[feed.ID]["folder name"]
        installed_version = feed_file[feed.ID]["installed version"]
        installed_version_description = feed_file[feed.ID][
            "installed_version_description"
        ]
        installation_status = feed_file[feed.ID]["installation status"]
    except:
        folder_name = ""
        installed_version = ""
        installed_version_description = ""
        installation_status = ""
    script_info = feed.script_info
    feed_file[feed.ID] = {
        "id": feed.ID,
        "url": feed.url,
        "name": script_info.name,
        "description": script_info.description,
        "latest version": script_info.version,
        "latest_version_description": script_info.version_description,
        "authors": script_info.authors,
        "relevant tags": feed.relevant_tags,
        "version list": feed.version_list,
        "version description list": feed.version_description_list,
        "is_main_branch": feed.is_main_branch(),
        "folder name": folder_name,
        "installed version": installed_version,
        "installed_version_description": installed_version_description,
        "installation status": installation_status,
        "raw_datetime": feed.raw_datetime,
    }

    # update feed file
    write_json(feed_file, GLOBAL_PATHS.feed_file)

    return script_info.known_feeds


def update_feeds():
    if DEVELOPMENT_MODE:
        pyegi_info = ScriptPyProject(GLOBAL_PATHS.pyegi_pyproject_file)
    else:
        pyegi_feed = FeedParser("https://github.com/SSgumS/Pyegi")
        pyegi_info = pyegi_feed.script_info
    checked_urls = []
    urls = pyegi_info.known_feeds
    main_known_feeds = [FeedParser(url, False) for url in urls]
    known_users = [feed.username for feed in main_known_feeds]
    known_users = np.unique(np.array(known_users)).tolist()
    username_2_count_dict: dict[str, int] = {}
    feeds_limit = 7
    while urls:
        url = urls[0]
        try:
            g = FeedParser(url)
        except:
            warnings.warn(f"Couldn't process feed {url}.")
            urls = urls[1:]
            continue
        is_known_user = True
        is_permitted_to_add_feeds = True
        username = g.username
        if username not in known_users:
            is_known_user = False
            try:
                feed_count = username_2_count_dict[username]
            except:
                feed_count = 0
                username_2_count_dict[username] = 0
            if feed_count >= feeds_limit:
                is_permitted_to_add_feeds = False
        url = g.url
        checked_urls.append(url)
        known_feeds = add_to_feed(g, main_known_feeds)
        # append known_feeds of the feed to urls
        if is_permitted_to_add_feeds:
            if not is_known_user:
                known_feeds = known_feeds[: feeds_limit - feed_count]  # type: ignore
                username_2_count_dict[username] += len(known_feeds)
            for known_feed in known_feeds:
                if known_feed not in checked_urls:
                    urls.append(known_feed)
        urls = urls[1:]


def download_script(g: FeedParser):
    script_id = g.ID
    script_name = g.script_name
    feed_file = FeedFile()
    script = feed_file.get_script(script_id)

    # folder name
    initial_folder_name = script.folder_name
    if not initial_folder_name:
        script_name_extractor = re.compile(r"^(.+)_\d+$")
        # check current dirs that exist
        i = 1
        all_sub_objects = os.listdir(GLOBAL_PATHS.scripts_dir)
        for entry in all_sub_objects:
            path = normal_path_join(GLOBAL_PATHS.scripts_dir, entry)
            if (match := script_name_extractor.search(entry)) and (
                match.group(1) == script_name
            ):
                i += 1
        # choose folder name
        folder_name = f"{script_name}_{i}"
    else:
        folder_name = initial_folder_name

    print(f"Preparing {script_id} links...")
    files, folders = g.get_files_and_folders()

    print(f"Creating {script_id} directories...")
    script_path = normal_path_join(GLOBAL_PATHS.scripts_dir, folder_name, is_dir=True)
    for folder in folders:
        path = normal_path_join(script_path, folder, is_dir=True)
        ensure_dir_tree(path)
    ensure_dir_tree(script_path)
    # update feed file
    script.folder_name = folder_name
    script.installed_version = g.script_info.version
    script.installed_version_description = g.script_info.version_description
    script.installation_status = InstallationStatus.W_DIRECTORIES
    feed_file.update_script(script)

    print(f"Downloading {script_id} files...")
    for file in files:
        file_download_url = g.get_download_url(file, g.folder_path)
        path = normal_path_join(script_path, file)
        was_in_keeps = False
        for entry in g.script_info.keeps:
            if file == entry:
                was_in_keeps = True
                break
            if file.startswith(normalize_path(entry, is_dir=True)):
                was_in_keeps = True
                break
        if (not was_in_keeps) or (not exists(path)):
            download_file(file_download_url, path)
    # update feed file
    script.installation_status = InstallationStatus.DOWNLOADED
    feed_file.update_script(script)


def ensure_init_file(script_id):
    feed_file = FeedFile()
    script = feed_file.get_script(script_id)
    script_path = script.folder

    init_path = script_path + "__init__.py"
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

    # update feed_file
    script.installation_status = InstallationStatus.W_PYEGI
    feed_file.update_script(script)


def install_script(g: FeedParser):
    script_id = g.ID

    old_py_version = clean_script_folder(script_id, g.script_info.keeps)
    download_script(g)
    ensure_init_file(script_id)
    new_py_version = install_pkgs(script_id)

    # cleanup old python's commons
    if old_py_version != new_py_version and old_py_version:
        clean_lib_links(old_py_version.common_dir)


def uninstall_script(script_id):
    print(f"Uninstalling {script_id}...")
    feed_file = FeedFile()
    script = feed_file.get_script(script_id)
    folder_name = script.folder_name
    if folder_name:
        script_path = script.folder
        # infer python
        py_result = infer_python_version(script_path + GLOBAL_PATHS.pyproject_filename)
        # remove dirs
        try:
            shutil.rmtree(script_path)
        except FileNotFoundError:
            pass
        # clean common-packages
        com_dir = normal_path_join(
            GLOBAL_PATHS.commons_dir, py_result.python_version.folder_name, is_dir=True
        )
        remove_script_from_lib_links(script_id, com_dir)
        clean_lib_links(com_dir)
    # update feed file
    script.folder_name = ""
    script.installed_version = ""
    script.installed_version_description = ""
    script.installation_status = InstallationStatus.UNKNOWN
    feed_file.update_script(script)


if __name__ == "__main__":
    scripts_names = [
        name
        for name in os.listdir(GLOBAL_PATHS.scripts_dir)
        if os.path.isdir(normal_path_join(GLOBAL_PATHS.scripts_dir, name))
    ]
    # url = "https://github.com/python-poetry/poetry-core/tree/1.1.0a6"
    url = "https://github.com/DrunkSimurgh/Pyegi_Scripts/tree/main/ColorMania"
    g = FeedParser(url)
    # install_script(g)
    # download_script(g)
    # for script in scripts_names:
    #     install_pkgs(script)
    # update_feeds()
