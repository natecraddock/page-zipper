import os
import shutil
import itertools

import utils
import widgets


def ungroup(merged):
    temp = []
    for p in merged:
        if type(p) is utils.PageGroup:
            temp.extend(p.pages)
        else:
            temp.append(p)

    return temp[:]


def copy_files(files, out, pre="img_"):
    progress = widgets.ProgressPopup("Saving Images", len(files))

    for i in range(len(files)):
        new_file = pre + str(str(i + 1).zfill(len(str(len(files)))) + os.path.splitext(files[i].path)[1]) #SUPER GROSS
        new_path = os.path.join(out, new_file)
        shutil.copy2(files[i].path, new_path)

        progress.next()
        progress.log_message("Copied {0} to {1}".format(files[i].path, new_path))

    progress.destroy()


def merge_lists(a, b):
    return [j for i in itertools.zip_longest(a, b) for j in i if j]


# Testing
def clear_dir(path):
    for f in os.listdir(path):
        os.remove(path + os.sep + f)
