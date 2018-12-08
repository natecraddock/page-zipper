# Page Zipper
[Download v1.1](https://github.com/natecraddock/page-zipper/releases/download/v1.1/Page.Zipper.v1.1.exe)

Page Zipper is a tool to aid in the document capture process. It is designed to merge (zip) right and left captured pages of books.

Page Zipper takes input from two folders, for the left and right pages, merges the pages like a zipper (right, left, right, left, right, left), and saves the images in a specified output directory.

## The Problem
At the [Shelby County Museum & Archive](https://shelbycountymuseum.com) we had been capturing images of the old courthouse records for over a year without a problem. We then encountered books too large to take pictures of! And we couldn't move the books side to side without damaging them.

## The Solution
We decided that capturing the right and left pages separately would be the easiest way to proceed. Page Zipper was created to merge the left and right pages together.

# How To Use Page Zipper
## Inputs
The `Input` tab contains two image thumbnail viewers. Page zipper takes two folders for input, one for left pages, and one for right pages. It assumes that the right page (cover) will go first.
To choose a folder, click `Browse`. Navigate and select the directory containing the images to zip. Repeat for the other side.

Select pages by clicking on the thumbnails. Select pages and click `Group` to group a set of pages together. Grouped pages will maintain the same order after the merge.
Click `Ungroup` after selecting a group to ungroup a set of pages.

## Outputs
In the `Output` tab a preview of the output is shown in order.
Specify an output directory by clicking `Browse`. A filename prefix can also be set. Click `Save` to save the files to the specified output directory.

## Utilities
In the `Utilities` tab there is a renamer. It allows a numerical rename of files in a folder.
The renamer also supports a filename prefix.
Clicking `Rename` will create a new folder in the same location as the chosen folder. Its name will be `<folder_name>_renamed`

## Help
The `Help` tab has a link to this readme, a support email, and a link to report issues.

# Building
## Dependencies
pyinstaller

`pip install pyinstaller`

To build a Windows executable

`pyinstaller -F -n "Page Zipper v1.1" --add-data="icon.ico;." --icon="icon.ico" __main__.py`

The executable file will be found in the dist directory

for rebuilds

`pyinstaller "Page Zipper v1.1.spec"` 

