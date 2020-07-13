#!/usr/bin/env python3

import os
import sys
import json
import glob
import re
import logging
import subprocess

from pathlib import Path

logger = logging.getLogger(__name__)

try:
    loglevel = getattr(logging, os.environ.get("LOGLEVEL", "INFO"))
except Exception:
    loglevel = logging.DEBUG

logger.setLevel(loglevel)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
if loglevel == logging.DEBUG:
    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
else:
    formatter = logging.Formatter("%(asctime)s\t%(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    import git
except Exception:
    logger.info("Using system git")
    git = False

GIT_BIN = os.environ.get("GIT_PATH", "/usr/bin/git")
MODULE_REPO_PATTERN = r'module.+"(.+)".*{.*\n.*source.*"(.+)".*\n'
MODULE_NAME_PATTERN = r"/.+/(.+)\.git\?ref=(.+)"


def repo_uri_to_module_path(repo_uri, name_pattern=MODULE_NAME_PATTERN):
    module_name, tag = re.findall(name_pattern, repo_uri).pop()
    return Path(".terraform/modules").joinpath(f"{module_name}_{tag}")


def repo_uri_to_tag(repo_uri, name_pattern=MODULE_NAME_PATTERN):
    _, tag = re.findall(name_pattern, repo_uri).pop()
    return tag


def clone_repo(repo_uri):
    repo_url = repo_uri.split("?")[0].lstrip("git::")
    module_path = repo_uri_to_module_path(repo_uri)
    try:
        tag = repo_uri_to_tag(repo_uri)
        if not git:
            proc = subprocess.run(
                [
                    GIT_BIN,
                    "clone",
                    "-q",
                    "-b",
                    tag,
                    "--depth",
                    "1",
                    "--",
                    repo_url,
                    f"{module_path}",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            if proc.returncode:
                if "already exists" in proc.stderr:
                    raise FileExistsError
                raise Exception(f"{GIT_BIN} failed with err:{proc.stderr}")
        else:
            module_path.mkdir(parents=True)
            git.Repo.clone_from(repo_url, module_path, branch=tag, depth=1)

    except FileExistsError:
        logger.debug(f"Already exists f{module_path}")


def main():
    module_inventory = {}

    for tf_file_path in glob.iglob("*.tf"):
        with (open(tf_file_path, "r")) as file:
            for module in re.finditer(MODULE_REPO_PATTERN, file.read()):
                module_inventory.update({module[1]: module[2]})

    module_repos = set(module_inventory.values())

    logger.info(f"All modules: {len(module_inventory)}")
    logger.info(f"To download: {len(module_repos)}")
    for repo in module_repos:
        clone_repo(repo)

    meta_file_path = Path(".terraform/modules/modules.json")
    meta_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_file_path, "w+") as meta_file:
        try:
            meta = json.load(meta_file)
        except json.decoder.JSONDecodeError:
            meta = None
        if not isinstance(meta, dict):
            meta = {}
        if "Modules" not in meta:
            meta.update({"Modules": []})
        for module_name, repo_uri in module_inventory.items():
            try:
                module_path = repo_uri_to_module_path(repo_uri)

                # tf12 format
                meta["Modules"].append(
                    {"Key": module_name, "Source": repo_uri, "Dir": f"{module_path}"}
                )
                # tf11 format
                meta["Modules"].append(
                    {
                        "Source": repo_uri,
                        "Key": f"1.{module_name};{repo_uri}",
                        "Version": "",
                        "Dir": f"{module_path}",
                        "Root": "",
                    }
                )
            except Exception:
                logger.exception(f"Unable to process {module_name}, repo {repo_uri}")

        json.dump(meta, meta_file, indent=2)


if __name__ == "__main__":
    main()
