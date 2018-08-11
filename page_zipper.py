# PageZipper v0.2
# Elder Nathan Craddock 2018

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import Image

import io
import os
import shutil

grouped_page_numbers = [8, 9, 10]

class Page:
    '''A page object that contains the path to an image file, and the loaded thumbnail of that file'''
    # TODO: Add thumbnail loading. This will allow the load_images function to tell if this file is a valid image or not
    def __init__(self, path):
        self.path = path

        self.thumb = self.make_thumbnail()

    def make_thumbnail(self):
        im = Image.open(self.path)
        size = 100, 100
        im.thumbnail(size)
        b = io.BytesIO()
        im.save(b, 'gif')
        return tk.PhotoImage(data=b.getvalue())


class PageGroup:
    '''An object that holds a group of pages'''
    def __init__(self, pages):
        self.pages = pages

    def print_pages(self):
        for p in self.pages:
            print(p)


class DirectoryBrowser(tk.Frame):
    '''A tkinter widget for a labeled directory browser'''
    def __init__(self, parent, label="Choose Folder:"):
        tk.Frame.__init__(self, parent)

        # Variable to access the entry text
        self.path = tk.StringVar()

        # Create GUI Elements for the Directory Browser Widget
        tk.Label(self, text=label).grid(column=0, row=0, sticky='nse')
        tk.Entry(self, textvariable=self.path).grid(column=1, row=0, sticky='nsew', padx=5)
        tk.Button(self, text="Browse", command=self.browse).grid(column=2, row=0, sticky='nse')

        # Weights
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

    def browse(self):
        directory = filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            self.path.set(directory)


class PageZipper:
    def __init__(self, root):
        self.root = root

        self.create_gui()

        self.validate_save()


    def validate_save(self):
        if self.info_label_left.valid and self.info_label_right.valid and self.info_label_output.valid:
            self.save_button['state'] = 'normal'
        else:
            self.save_button['state'] = 'disabled'

    def create_gui(self):
        root.title("Page Zipper v0.2")

        # Disable tearing for the menubar
        root.option_add('*tearOff', 'FALSE')

        # Create Menu Bar
        self.menubar = tk.Menu(self.root)
        self.menu_file = tk.Menu(self.menubar)
        #self.menu_edit = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)

        self.menu_file.add_command(label='Exit', command=self.on_quit)

        self.menubar.add_cascade(menu=self.menu_file, label='File')
        #self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menubar.add_cascade(menu=self.menu_help, label='Help')

        self.root.config(menu=self.menubar)


        # Create Left Page Frame
        self.left_pages = tk.Frame(self.root)
        self.left_pages.grid(row=0, column=0, sticky='nesw')

        tk.Label(self.left_pages, text="Left Pages").grid(row=0, column=0, sticky='nsw', padx=10)
        self.browser_left = DirectoryBrowser(self.left_pages, "Path:")
        self.info_label_left = tk.Label(self.left_pages, text="Select a path")
        self.info_label_left.valid = False
        self.info_label_left.pages = []

        self.browser_left.grid(row=1, column=0, sticky='nesw', padx=10)
        self.info_label_left.grid(row=2, column=0, sticky='nsw', padx=10)

        self.left_pages.columnconfigure(0, weight=1)


        ttk.Separator(self.root, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=10)


        # Create Right Page Frame
        self.right_pages = tk.Frame(self.root)
        self.right_pages.grid(row=2, column=0, sticky='nesw')

        tk.Label(self.right_pages, text="Right Pages").grid(row=0, column=0, sticky='nsw', padx=10)
        self.browser_right = DirectoryBrowser(self.right_pages, "Path:")
        self.info_label_right = tk.Label(self.right_pages, text="Select a path")
        self.info_label_right.valid = False
        self.info_label_right.pages = []

        self.browser_right.grid(row=1, column=0, sticky='nesw', padx=10)
        self.info_label_right.grid(row=2, column=0, sticky='nsw', padx=10)

        self.right_pages.columnconfigure(0, weight=1)


        ttk.Separator(self.root, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=10)


        # Create Output Frame
        self.output = tk.Frame(self.root)
        self.output.grid(row=4, column=0, sticky='nesw')

        tk.Label(self.output, text="Output").grid(row=0, column=0, sticky='nsw', padx=10)
        self.browser_output = DirectoryBrowser(self.output, "Path:")
        self.info_label_output = tk.Label(self.output, text="Select a path")
        self.info_label_output.valid = False
        self.info_label_output.pages = []

        self.save_button = tk.Button(self.output, text="Save", command=self.save_files)

        self.browser_output.grid(row=1, column=0, sticky='nesw', padx=10)
        self.info_label_output.grid(row=2, column=0, sticky='nsw', padx=10)
        self.save_button.grid(row=3, column=0, sticky='ew')

        self.output.columnconfigure(0, weight=1)

        # For horizontal expanding of all widgets
        self.root.columnconfigure(0, weight=1)

        # Add callbacks for entry validation
        self.browser_left.path.trace('w',  lambda name, index, mode, label=self.info_label_left, sv=self.browser_left.path:self.validate_input(sv, label))
        self.browser_right.path.trace('w',  lambda name, index, mode, label=self.info_label_right, sv=self.browser_right.path:self.validate_input(sv, label))
        self.browser_output.path.trace('w',  lambda name, index, mode, label=self.info_label_output, sv=self.browser_output.path:self.validate_output(sv, label))


    def on_quit(self):
        quit()

    def load_images(self, directory):
        paths = os.listdir(directory)
        paths.sort()

        return [Page(directory + os.sep + path) for path in paths]

    def validate_input(self, path, label):
        path = path.get()
        label.valid = False
        if path == "":
            label['text'] = "Select a path"
        else:
            # Check if path is real
            if os.path.exists(path):
                # Check for images in folder
                label.pages = self.load_images(path)
                if label.pages:
                    label['text'] = "Found " + str(len(label.pages)) + " images"
                    label.valid = True
                else:
                    label['text'] = "No images found"
                #self.valid = True
            else:
                label['text'] = "Invalid path"
        self.validate_save()

    def validate_output(self, path, label):
        label.valid = False
        path = path.get()
        if path == "":
            label['text'] = "Select a path"
        else:
            # Check if path is real
            if os.path.exists(path):
                label['text'] = "Valid output"
                label.valid = True
            else:
                label['text'] = "Invalid path"
        self.validate_save()

    def group(self):
        # This might be easier to do if you just pop the length of list and start at n
        first_index = grouped_page_numbers[0] - 1

        pages = [self.info_label_left.pages.pop(first_index) for i in reversed(grouped_page_numbers)]
        for p in pages:
            print(p.path)

        group = PageGroup(pages)

        # Replace the grouped pages with the page group
        self.info_label_left.pages.insert(first_index, group)

    def ungroup(self, merged):
        temp = []
        for p in merged:
            if type(p) is PageGroup:
                temp.extend(p.pages)
            else:
                temp.append(p)

        return temp

    def copy_files(self, files, out, pre="img_"):
        for i in range(len(files)):
            new_file = pre + str(str(i + 1).zfill(len(str(len(files)))) + os.path.splitext(files[i].path)[1]) #SUPER GROSS
            new_path = os.path.join(out, new_file)
            shutil.copy2(files[i].path, new_path)
            #print("Created file", new_path)

    def save_files(self):
        print("TESTING: Clear output")
        self.clear_dir(self.browser_output.path.get())

        print("GROUPING PAGES")
        # This is a lot of hard-coding to handle a certain case
        self.group()

        print("MERGING PAGE LISTS")
        merged = self.merge_lists(self.info_label_right.pages, self.info_label_left.pages)

        print("UNGROUPING PAGES")
        merged = self.ungroup(merged)

        print("COPYING FILES")

        self.copy_files(merged, self.browser_output.path.get())


    def merge_lists(self, a, b):
        return [j for i in zip(a, b) for j in i]

    # Testing
    def clear_dir(self, path):
        for f in os.listdir(path):
            os.remove(path + os.sep + f)


# Start the GUI
root = tk.Tk()
PageZipper(root)

root.update()
#root.minsize(root.winfo_width() + 250, root.winfo_height() + root.menubar.winfo_reqheight())
#root.minsize(root.winfo_width() + 250, root.winfo_reqheight())
#root.resizable(width=True, height=False)
root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
root.resizable(width=True, height=True)
root.mainloop()
