#!/usr/bin/python

"""
This script should simplify modding of Lethal Company
  without installing any WiNdOWs oNlY sTuPiD StUfF

In Lethal Company directory:
  - run the script
  - copy and replace old files in game directory with the new content in .mods

If you have installed Steam via Flatpak, then the path is:
  ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Lethal Company/
"""

import os
import re
import zipfile
from typing import List
import logging
import shutil
from collections import OrderedDict
import sys
import time
import requests

try:
    import requests_cache
except ImportError:
    requests_cache_installed = False
else:
    requests_cache_installed = True

# LOG_LEVEL = logging.DEBUG
LOG_LEVEL = logging.INFO

logging.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)
script_dir = os.path.dirname(os.path.realpath(__file__))
# keep up-to-date version of mods in here
mods_dir = os.path.join(script_dir, "up-to-date-mods")
# place for old and obsolete mods
old_mods_dir = os.path.join(script_dir, "old")
# move this into your game
new_mods_dir = os.path.join(script_dir, "new-mod-dir")

# Files to ignore
file_blacklist = [
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "icon.png",
    "manifest.json",
]

# Mod have inconsistent directory structures
#   files or directories can be compared to this dictionary to see where they should be placed
#   NOTE: some even have everything in their own directory named after the mod
#         for example BepInExPack
#   NOTE: items are sorted by priority (the most import first, least important last)
prefix_dict = OrderedDict(
    {
        "BepInEx": "",
        "plugins": "BepInEx",
        ".*\.dll": "BepInEx/plugins",
        "config": "BepInEx",
        "patchers": "BepInEx",
        "yippeesound": "BepInEx/plugins",
    }
)


def mkdir(path: str) -> None:
    """mkdir -p"""
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


# requests_cache.install_cache('thunderstore_cache', expire_after=360)
if requests_cache_installed:
    requests_cache.install_cache(
        os.path.join(script_dir, "thunderstore_cache"),
        expire_after=360,
    )


class Mod:
    """Class representing a single mod"""

    def __init__(self, url: str):
        self.url = url
        self.name = os.path.basename(os.path.dirname(url))
        self.timeout = 5

        self.__get_page__()
        self.download_url = ""
        self.__get_download_link__()
        self.version = os.path.basename(self.download_url)
        self.modname = f"{self.name}-{self.version}"

        # filename to be downloaded
        self.filename = f"{self.modname}.zip"
        # path to downloaded file
        self.filepath = os.path.join(mods_dir, self.filename)
        # directory where to unzip the zip file
        self.dirpath = os.path.join(mods_dir, self.modname)

        # list of all dependencies
        self.deps: List[str] = []

        self.print()

    def print(self) -> None:
        """Print attributes"""
        logging.debug("name:       %s", self.name)
        logging.debug("  url:      %s", self.url)
        logging.debug("  download: %s", self.download_url)
        logging.debug("  version:  %s", self.version)
        logging.debug("  modname:  %s", self.modname)
        logging.debug("  filename: %s", self.filename)
        logging.debug("  filepath: %s", self.filepath)
        logging.debug("  deps:     ")
        for i in self.deps:
            logging.debug("    - %s", i)

    def __get_page__(self) -> None:
        """Download a HTML page as list of strings"""
        self.page = requests.get(self.url, timeout=self.timeout).text

    def __get_download_link__(self) -> None:
        """Search the downloaded page and look for download link with recent version"""
        line = re.findall(r".*/package/download/.*", self.page)[0]
        link = re.sub(r'.*href="', r"", line)
        link = re.sub(r'[\/]?".*', r"", link)
        self.download_url = link

    def get_dependencies(self) -> list[str]:
        """Search the downloaded page and look for dependencies"""
        found_deps_section = False
        for line in self.page.splitlines():
            if re.match(r".*This mod requires the following mods to function.*", line):
                found_deps_section = True
            if found_deps_section:
                if re.match(r".*h5 class.*/c/lethal-company/p/.*", line):
                    new_link = re.sub(r'.*href="', r"https://thunderstore.io", line)
                    new_link = re.sub(r'">.*', r"", new_link)
                    self.deps.append(new_link)
                if re.match(r"^</div>.*", line):
                    break
        return self.deps

    def __download__(self) -> None:
        """Download mod ZIP file"""
        if os.path.isfile(self.filepath):
            logging.debug("  ... file already downloaded")
        else:
            logging.debug("  ... downloading")
            response = requests.get(self.download_url, timeout=self.timeout)
            if response.ok is not True or response.status_code != 200:
                logging.error("Downloading failed")

            with open(self.filepath, mode="wb") as file:
                file.write(response.content)

    def __unzip__(self) -> None:
        """Unzip downloaded file"""
        if os.path.isdir(self.dirpath):
            logging.debug("  ... file already extracted")
            return
        if os.path.isfile(self.filepath):
            logging.debug("  ... extracting")
            with zipfile.ZipFile(self.filepath, "r") as zip_ref:
                zip_ref.extractall(self.dirpath)

    def __remove_old_versions__(self) -> None:
        """Move old mod versions into old directory"""
        all_items = os.listdir(mods_dir)
        for item in all_items:
            if re.match(f"{self.name}.*", item) and not re.match(
                f"{self.modname}", item
            ):
                logging.debug("  ... trashing %s", item)
                shutil.move(os.path.join(mods_dir, item), old_mods_dir)

    def __merge__(self, mod_rootpath: str | None = None, dry_run: bool = True) -> None:
        """
        Copy the extracted mod files into staging directory with other mods

        This one is a big mess. Biggest problem being the inconsistency in mods.
        A lot of guess-work and assumptions are made in here.
        """
        if mod_rootpath is None:
            mod_rootpath = self.dirpath

        # get list of extracted items without blacklisted garbage
        all_items = [f for f in os.listdir(mod_rootpath) if f not in file_blacklist]

        # figure out directory prefix
        _prioritized_patterns = list(prefix_dict.keys())
        prefix_dst = ""
        _prefix_index = sys.maxsize
        for item in all_items:
            for _pattern, _prefix in prefix_dict.items():
                if re.match(_pattern, item):
                    # it match found, check if is has higher priority than previous match
                    _this_index = _prioritized_patterns.index(_pattern)
                    if _prefix_index > _this_index:
                        _prefix_index = _this_index
                        prefix_dst = _prefix

        # for each file or directory in mod, try to copy it into destination
        for item in all_items:
            item_path = os.path.join(mod_rootpath, item)

            # if a directory is named after the mod itself, dive into it
            #   (this is a problem with BepInEx mod for example where the 'BepInEx' is nested in 'BepInExPack')
            if os.path.isdir(item_path) and re.match(f"{self.name}.*", item):
                # recursion to deal with nested directories
                self.__merge__(
                    mod_rootpath=item_path,
                    dry_run=dry_run,
                )
                continue

            dest_dir = os.path.join(new_mods_dir, prefix_dst)
            logging.info(
                "[%s] copy '%s'\t-> '%s'",
                self.name.ljust(25),
                item,
                os.path.join(prefix_dst, item),
            )

            if dry_run:
                continue
            mkdir(dest_dir)
            # copy
            if os.path.isfile(item_path):
                # if file, just copy
                shutil.copy(
                    item_path,
                    dest_dir,
                )
            else:
                # if directory, copy recursively
                shutil.copytree(
                    item_path,
                    os.path.join(dest_dir, item),
                    dirs_exist_ok=True,
                )

    def get(self) -> None:
        """Get the mod"""
        self.__remove_old_versions__()
        self.__download__()
        self.__unzip__()
        self.__merge__(dry_run=False)


def main() -> None:
    """Main function"""

    # create directories
    mkdir(mods_dir)
    mkdir(old_mods_dir)

    # trash old mods dir
    if os.path.isdir(new_mods_dir):
        new_name = "{}--{}".format(
            os.path.basename(new_mods_dir),
            time.time(),
        )
        shutil.move(
            new_mods_dir,
            os.path.join(old_mods_dir, new_name),
        )
        mkdir(new_mods_dir)

    # load file listing all the mods
    modfile_path = os.path.join(script_dir, "mods.txt")
    with open(modfile_path, "r", encoding="utf-8") as modfile:
        # strip newline characted from each line
        mods = [i.rstrip() for i in modfile.readlines()]

    # iterate over mods and get them
    for mod in mods:
        my_mod = Mod(url=mod)
        my_mod.get()

        # get dependencies
        deps = my_mod.get_dependencies()
        for dep in deps:
            if dep not in mods:
                mods.append(dep)


if __name__ == "__main__":
    main()
