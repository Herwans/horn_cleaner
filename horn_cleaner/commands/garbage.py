import os
import pathlib
import re

import click

from horn_cleaner.utils import prompt, utils
from horn_cleaner.utils.config import Configuration
from horn_cleaner.utils.path import Path

to_delete = Configuration().get_delete_pattern()


@click.command()
@click.argument("folder")
@click.option("--apply", "-a", is_flag=True, default=False, help="Apply the change")
@click.option("--sub", "-s", is_flag=True, default=False, help="Apply to the folder and it's sub folders")
def garbage(folder, apply, sub):
    """Remove empty folders, delete unwanted elements"""

    clean(folder, apply)

    if sub:
        for element in Path(folder).folders():
            clean(element, apply)
            move(element, apply)
            delete(element, apply)


def clean(folder, apply):
    """Remove elements which match regex to be deleted"""
    for element in Path(folder).files():
        if is_to_delete(element):
            if apply:
                os.remove(element)
                prompt.alert(f"{element} deleted")
            else:
                prompt.alert(f"{element} is candidate to deletion")


def move(folder, apply):
    """Empty folder when no other files nor folders present"""
    path = Path(folder)

    if path.count() == 0 or len(path.folders()) > 0:
        return
    elements = path.files()
    total = path.count()
    videos = 0
    for element in elements:
        if utils.is_video(element):
            videos = videos + 1

    if videos == total:
        if apply:
            for element in elements:
                current = Path(element)
                if not pathlib.Path(f"{folder}{os.sep}..{os.sep}{current.name()}").exists():
                    current.move(f"..{os.sep}{current.name()}")
            if path.count() == 0:
                prompt.info(f"{folder} has been emptied")
            else:
                prompt.alert(f"{folder} can't be emptied")
        else:
            prompt.info(f"{folder} is candidate to simplification")


def delete(folder, apply):
    """Delete folder when empty"""
    path = Path(folder)
    if path.count() == 0:
        utils.delete_folder(folder)


def is_to_delete(element):
    for pattern in to_delete:
        if re.search(pattern, element) is not None:
            return True
    return False
