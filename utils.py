import tkinter as tk
import tempfile
import os
import shutil
import sys
from PIL import Image
import io

import widgets


class Page:
    '''A page object that contains the path to an image file, and the loaded thumbnail of that file'''

    size = 250

    def __init__(self, path):
        self.path = path
        self.name = os.path.splitext(os.path.basename(self.path))[0]
        self.thumb = self.make_thumbnail()

    # Returns None if no image can be loaded
    def make_thumbnail(self):
        try:
            image = Image.open(self.path)
            image.thumbnail((Page.size, Page.size))
            b = io.BytesIO()
            image.save(b, 'gif')
            return tk.PhotoImage(data=b.getvalue())

        except (OSError, IsADirectoryError) as err:
            print("Error Loading Image: {0}".format(err))
            return None


# TODO: include group image
class PageGroup:
    '''An object that holds a group of pages'''
    def __init__(self, pages):
        self.pages = pages
        self.name = "Group"


def _create_backup(files, path):
    backup = tempfile.TemporaryDirectory()

    for file in files:
        origin = os.path.join(path, file)
        destination = os.path.join(backup.name, file)

        if os.path.isfile(origin):
            shutil.copy2(origin, destination)
        else:
            shutil.copytree(origin, destination)

    return backup


def _restore_backup(backup, path):
    if os.path.exists(path):
        shutil.rmtree(path)

    shutil.copytree(backup.name, path)


def rename_files(path, start_number, prefix):
    files = os.listdir(path)
    files.sort()

    progress = widgets.ProgressPopup("Renaming Files", len(files))
    progress.log_message("Creating backup")

    backup = _create_backup(files, path)

    digits = len(os.listdir(path)) + start_number

    # Create temporary directory for renaming
    renamed_directory = path + "_renamed"
    if os.path.exists(renamed_directory):
        shutil.rmtree(renamed_directory)
    os.mkdir(renamed_directory)

    try:
        progress.log_message("Copying Files")
        # Move all of the files to a new directory, with new names
        for file in files:
            origin = os.path.join(path, file)
            if os.path.isfile(origin):
                end = os.path.splitext(file)[1]
                file_name = str(start_number).zfill(len(str(digits))) + end
                file_name = prefix + file_name
                dest = os.path.join(renamed_directory, file_name)

                shutil.copyfile(origin, dest)
                progress.next()
                progress.log_message("Renamed {0} as {1}".format(origin, file_name))

                start_number += 1
            else:
                dest = os.path.join(renamed_directory, file)
                shutil.copytree(origin, dest)
                progress.next()
                progress.log_message("Did not modify {0}".format(origin))

        progress.log_message("Rename Completed")

    except:
        progress.log_message("Rename failed, restoring backup")
        _restore_backup(backup, path)

    progress.destroy()
