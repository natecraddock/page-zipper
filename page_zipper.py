# PageZipper v1.0
# Nathan Craddock 2018

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font

from PIL import Image

import io
import sys
import os
import shutil
import itertools
import webbrowser
import tempfile

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


# TODO: bring back and include group image
class PageGroup:
    '''An object that holds a group of pages'''
    def __init__(self, pages):
        self.pages = pages
        self.name = "Group"


class ProgressPopup(tk.Toplevel):
    '''Displays progress with progressbar'''
    def __init__(self, title, steps=100):
        tk.Toplevel.__init__(self)
        self.fixed_font = Font(size=10)
        self.line_height = self.fixed_font.metrics("linespace")

        self.title(title)
        tk.Label(self, text=title).grid(row=0, column=0, sticky='w', padx=5, pady=20, columnspan=2)
        self.progress = ttk.Progressbar(self, orient='horizontal', length=200, mode='determinate', maximum=100)
        self.progress.grid(row=1, column=0, sticky='ew', padx=5, columnspan=2)

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=2, column=1, sticky='nesw', pady=10)

        self.log = tk.Canvas(self, background='#FFFFFF', width=500, height=150, yscrollcommand=self.scrollbar.set)
        self.log.grid(row=2, column=0, sticky='nesw', pady=10)
        self.log.line_number = 0

        self.scrollbar.config(command=self.log.yview)

        self.grab_set()

        self.step = 100.0 / steps

    def next(self):
        self.progress['value'] += self.step
        self.update()

    def log_message(self, line):
        self.log.create_text(0, (self.line_height * self.log.line_number), font=self.fixed_font, text=line, anchor='nw')
        self.log.line_number += 1
        self.log.configure(scrollregion=self.log.bbox('all'))
        self.log.yview_moveto(1)

        self.update()

class RenameFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.number = tk.IntVar()
        self.number.set(1)

        self.browser = DirectoryBrowser(self, "Rename files in folder:")
        self.browser.grid(row=0, column=0, sticky='nesw', padx=5, columnspan=2)

        self.label = tk.Label(self, text="Starting Number:").grid(column=0, row=1, sticky='nswe')
        self.entry = tk.Entry(self, textvariable=self.number).grid(column=1, row=1, sticky='nsew', padx=5, pady=5)

        self.rename_button = tk.Button(self, text='Rename Files', command=self.rename)
        self.rename_button.grid(row=2, column=0, columnspan=2, sticky='nesw', padx=5)

    def rename(self):
        f = self.browser.path.get()
        n = self.number.get()

        if os.path.exists(f) and len(os.listdir(f)) > 0:
            self.rename_files(f, n)

    # Renames files (numerically) in "files_in" with base path
    def rename_files(self, path, n):
        files_in = os.listdir(path)
        p = path
        count = n
        files = files_in[:]
        files.sort()

        progress = ProgressPopup("Renaming Files", len(files))
        progress.log_message("Creating backup")

        backup = tempfile.TemporaryDirectory()

        # Copy dir as well
        for f in files:
            if os.path.isfile(os.path.join(p, f)):
                origin = os.path.join(p, f)
                destination = os.path.join(backup.name, f)
                shutil.copy2(origin, destination)
            else:
                origin = os.path.join(p, f)
                destination = os.path.join(backup.name, f)
                shutil.copytree(origin, destination)

        digits = len(os.listdir(p)) + count

        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                progress.log_message("Copying Files")
                # Move all of the files to a new directory, with new names
                for f in files:
                    if os.path.isfile(os.path.join(p, f)):
                        end = os.path.splitext(f)[1]
                        origin = os.path.join(p, f)
                        new_name = str(count).zfill(len(str(digits))) + end
                        dest = os.path.join(temporary_directory, new_name)

                        os.rename(origin, dest)
                        progress.next()
                        progress.log_message("Renamed {0} as {1}".format(origin, new_name))

                        count += 1
                    else:
                        origin = os.path.join(p, f)
                        dest = os.path.join(temporary_directory, f)
                        shutil.copytree(origin, dest)
                        progress.next()
                        progress.log_message("Did not modify {0}".format(origin))

                # Replace old directory with temporary directory
                try:
                    print(p)
                    #os.rmdir(p)
                    shutil.rmtree(p)
                except:
                    print("No dir to remove")

                progress.log_message("Saving")
                shutil.copytree(temporary_directory, p)

            except:
                progress.log_message("Rename failed, restoring backup")
                shutil.rmtree(p)
                shutil.copytree(backup.name, p)

            progress.destroy()

class HelpFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        tk.Label(parent, text="Page Zipper v1.0", font=("tkdefaultfont", 18)).grid(row=0, pady=10)

        text = "Page Zipper is a tool to aid in the document capture process. It is designed to merge (zip) right and left captured pages of books."
        tk.Message(parent, text=text, width=600).grid(row=1, pady=10)

        readme = tk.Label(parent, text="View the Readme on GitHub", fg='blue', cursor='hand2')
        readme.bind("<Button-1>", lambda e, l=r'https://github.com/natecraddock/page-zipper/': webbrowser.open(l))
        readme.grid(row=2, pady=5, sticky='ew')


        issue = tk.Label(parent, fg="blue", text="Report an issue on GitHub", cursor="hand2")
        issue.bind("<Button-1>", lambda e, l=r'https://github.com/natecraddock/page-zipper/issues': webbrowser.open(l))
        issue.grid(row=3, pady=5, sticky='ew')

        tk.Label(parent, text="If you need help, email me at:").grid(row=4, pady=10)

        email = tk.Label(parent, text="nzcraddock@gmail.com (click to copy to clipboard)", fg="blue", cursor="hand2")
        email.bind("<Button-1>", lambda _: self.clip())
        email.grid(row=5, pady=5, sticky='ew')

    def clip(self):
        self.clipboard_clear()
        self.clipboard_append('nzcraddock@gmail.com')
        self.update()

class PrefixEntry(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.prefix = tk.StringVar()
        self.prefix.set('img_')

        tk.Label(self, text="File Prefix:").grid(column=0, row=0, sticky='nse')
        tk.Entry(self, textvariable=self.prefix).grid(column=1, row=0, sticky='nsew', padx=5)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)


class DirectoryBrowser(tk.Frame):
    '''A tkinter widget for a labeled directory browser'''
    def __init__(self, parent, label="Choose Folder:", callback=lambda:None):
        tk.Frame.__init__(self, parent)

        self.callback = callback

        # Variable to access the entry text
        self.path = tk.StringVar()

        # Create GUI Elements for the Directory Browser Widget
        tk.Label(self, text=label).grid(column=0, row=0, sticky='nse')
        tk.Entry(self, textvariable=self.path, state='readonly').grid(column=1, row=0, sticky='nsew', padx=5)
        tk.Button(self, text="Browse", command=self.browse).grid(column=2, row=0, sticky='nse')

        # Weights
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

    def browse(self):
        directory = filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            if os.path.exists(directory):
                self.path.set(directory)
                self.callback()


class ThumbnailViewer(tk.Frame):
    '''A frame that holds a canvas for loaded images. Can scroll horizontally'''
    def __init__(self, root, group=False, callback=lambda:None, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.pages_in = []
        self.pages = []
        self.hit_boxes = []
        self.selected = []
        self.scroll_location = None
        self.callback = callback

        self.canvas = tk.Canvas(self, background='#FFFFFF', height=int(Page.size * 0.85), width=800)
        self.scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky='ew', columnspan=2)
        self.scrollbar.grid(row=1, column=0, sticky='nesw', columnspan=2)

        if group:
            frame = tk.Frame(self, bd=0)
            frame.grid(row=2, column=0, sticky='w', pady=5)
            tk.Button(frame, text='Group', command=self.group).grid(row=0, column=0, sticky='w')
            tk.Button(frame, text='Ungroup', command=self.ungroup).grid(row=0, column=1, sticky='w')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind("<Button-1>", self.on_click)
        self.slider = self.scrollbar.get()

    def reload_pages(self, pages_in=None):
        if pages_in is not None:
            self.pages_in = pages_in
        self.pages = self.pages_in[:]
        self.update()

    def update(self):
        self.selected = []
        self.draw()
        self.callback()

    def draw(self):
        # CLEAR ALL
        self.canvas.delete('all')
        self.hit_boxes = []
        self.scroll_location = self.scrollbar.get()

        for i, page in enumerate(self.pages):
            spacing = 20
            size = Page.size
            n = str(i + 1).zfill(len(str(len(self.pages))))

            # Create a frame for the image and text and save it to a list
            box = (size * i) + (i * spacing), 1, (size * i) + (i * spacing) + size, Page.size + 25
            if i in self.selected:
                self.canvas.create_rectangle(box, fill='lightblue', outline='', tags="background")

            if type(page) is Page:
                name = n + "  " + page.name
                self.canvas.create_image((size * i) + (i * spacing), spacing / 2, image=page.thumb, anchor="nw")
                self.canvas.create_text((size * i) + (i * spacing) + (size / 2), int(size * 0.75), font=("tkdefaultfont", 10), text=name, anchor="n")
            elif type(page) is PageGroup:
                # Draw first page of the group
                self.canvas.create_image((size * i) + (i * spacing), spacing / 2, image=page.pages[0].thumb, anchor="nw")
                self.canvas.create_text((size * i) + (i * spacing) + (size / 2), int(size * 0.75), font=("tkdefaultfont", 10), text=n + " " + page.name)

            self.hit_boxes.append(self.canvas.create_rectangle(box, fill='', outline='', tags="hitbox"))

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.scrollbar.set(self.scroll_location[0], self.scroll_location[1])

    def on_click(self, event):
        item = self.canvas.find_withtag('current')

        # Page selected
        if 'hitbox' in self.canvas.gettags(item):
            index = self.hit_boxes.index(item[0])

            if not index in self.selected:
                self.selected.append(index)
            else:
                self.selected.remove(index)

            self.selected.sort()
            self.draw()

    # TODO: Groups don't handle gaps well
    def group(self):
        if self.selected:
            first_index = self.selected[0]

            group = PageGroup([self.pages.pop(first_index) for i in reversed(self.selected)])

            # Replace the grouped pages with the page group
            self.pages.insert(first_index, group)
            self.update()

    def ungroup(self):
        if self.selected:
            temp = []
            for p in self.pages:
                if type(p) is PageGroup and self.pages.index(p) in self.selected:
                    temp.extend(p.pages)
                else:
                    temp.append(p)

            self.pages = temp[:]
            self.update()

class PageGrouper(ThumbnailViewer):
    def __init__(self, root, *args, **kwargs):
        ThumbnailViewer.__init__(self, root, *args, **kwargs)


class PageZipper:
    def __init__(self, root):
        self.root = root
        root.title("Page Zipper v1.0")
        #root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file="icon.png"))

        # Create dictionary variables for the three UI areas
        self.left = {'valid':False, 'pages':[]}
        self.right = {'valid':False, 'pages':[]}
        self.utils = {}
        self.output = {'valid':False, 'pages':[]}

        self.create_gui()

    def create_gui(self):
        # Create the frames and separators to pack UI elements into
        self.notebook = ttk.Notebook(self.root)
        self.input_tab = tk.Frame(self.notebook)
        self.output_tab = tk.Frame(self.notebook)
        self.utils_tab = tk.Frame(self.notebook)
        self.help_tab = tk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")
        self.notebook.add(self.output_tab, text="Output")
        self.notebook.add(self.utils_tab, text="Utilities")
        self.notebook.add(self.help_tab, text="Help")
        self.notebook.grid(row=0, column=0, sticky='nesw')

        HelpFrame(self.help_tab).grid(row=0, column=0, sticky='nesw')

        # Create frames for each area
        self.left['frame'] = tk.Frame(self.input_tab)
        self.left['frame'].grid(row=0, column=0, sticky='nesw', pady=15)
        ttk.Separator(self.input_tab, orient="horizontal").grid(row=1, column=0, sticky="ew")
        self.right['frame'] = tk.Frame(self.input_tab)
        self.right['frame'].grid(row=2, column=0, sticky='nesw', pady=15)
        self.utils['frame'] = tk.Frame(self.utils_tab)
        self.utils['frame'].grid(row=0, column=0, sticky='nesw', pady=15)
        self.output['frame'] = tk.Frame(self.output_tab)
        self.output['frame'].grid(row=0, column=0, sticky='nesw', pady=10)

        # Fill Left Pages Frame
        self.left['browser'] = DirectoryBrowser(self.left['frame'], "Left Pages:")
        self.left['viewer'] = ThumbnailViewer(self.left['frame'], group=True, callback=self.on_viewer_update)
        self.left['browser'].grid(row=0, column=0, sticky='nesw', padx=10)
        self.left['viewer'].grid(row=1, column=0, sticky='nesw', padx=10, pady=5)
        self.left['frame'].columnconfigure(0, weight=1)

        # Fill Right Pages Frame
        self.right['browser'] = DirectoryBrowser(self.right['frame'], "Right Pages:")
        self.right['viewer'] = ThumbnailViewer(self.right['frame'], group=True, callback=self.on_viewer_update)
        self.right['browser'].grid(row=0, column=0, sticky='nesw', padx=10)
        self.right['viewer'].grid(row=1, column=0, sticky='nesw', padx=10, pady=5)
        self.right['frame'].columnconfigure(0, weight=1)

        # Fill Utilities Frame
        self.utils['renamer'] = RenameFrame(self.utils['frame'])
        self.utils['renamer'].grid(row=0, column=0, sticky='nesw')
        self.utils['renamer'].columnconfigure(0, weight=1)

        # Fill Output Frame
        self.output['viewer'] = ThumbnailViewer(self.output['frame'])
        self.output['browser'] = DirectoryBrowser(self.output['frame'], "Output Path:")
        self.save_button = tk.Button(self.output['frame'], text="Save", command=self.save_files)
        self.output['viewer'].grid(row=0, column=0, sticky='nesw', padx=10, pady=5)
        self.output['browser'].grid(row=1, column=0, sticky='nesw', padx=10)

        self.output['prefix'] = PrefixEntry(self.output['frame'])
        self.output['prefix'].grid(row=2, column=0, sticky='nsw', padx=10, pady=5)

        self.save_button.grid(row=3, column=0, sticky='', pady=5)
        self.output['frame'].columnconfigure(0, weight=1)

        # For horizontal expanding of all widgets
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)
        self.input_tab.columnconfigure(0, weight=1)
        self.output_tab.columnconfigure(0, weight=1)
        self.help_tab.columnconfigure(0, weight=1)
        self.utils_tab.columnconfigure(0, weight=1)

        # Set callbacks to load images that are called when path is valid
        self.left['browser'].callback = lambda area=self.left : self.on_input(area)
        self.right['browser'].callback = lambda area=self.right : self.on_input(area)

    def on_viewer_update(self):
        merged = self.merge_lists(self.right['viewer'].pages, self.left['viewer'].pages)
        merged = self.ungroup(merged)

        # Rename TODO: Its broken!
        #for i, p in enumerate(merged):
        #    p.name = "page_" + str(str(i + 1).zfill(len(str(len(merged)))) + os.path.splitext(p.path)[1])

        self.output['viewer'].reload_pages(merged)

    # Create a toplevel widget that displays a progressbar as the pages are loaded
    def load_pages(self, directory):
        paths = os.listdir(directory)
        paths.sort()

        progress = ProgressPopup("Loading Pages", len(paths))

        temp = []
        for path in paths:
            if not os.path.isdir(os.path.join(directory, path)):
                p = Page(os.path.join(directory, path))

                if p.thumb is not None:
                    temp.append(p)
                progress.next()
                progress.log_message("Created thumbnail for {}".format(path))

        progress.destroy()

        return temp

    def on_input(self, area):
        path = area['browser'].path.get()

        # Load pages, then draw in ImageViewer
        area['pages'] = self.load_pages(path)

        if area['pages']:
            area['viewer'].reload_pages(area['pages'])

    def ungroup(self, merged):
        temp = []
        for p in merged:
            if type(p) is PageGroup:
                temp.extend(p.pages)
            else:
                temp.append(p)

        return temp[:]

    def copy_files(self, files, out, pre="img_"):
        progress = ProgressPopup("Saving Images", len(files))

        for i in range(len(files)):
            new_file = pre + str(str(i + 1).zfill(len(str(len(files)))) + os.path.splitext(files[i].path)[1]) #SUPER GROSS
            new_path = os.path.join(out, new_file)
            shutil.copy2(files[i].path, new_path)

            progress.next()
            progress.log_message("Copied {0} to {1}".format(files[i].path, new_path))

        progress.destroy()

    def save_files(self):
        output_path = self.output['browser'].path.get()
        if self.left['viewer'].pages and self.right['viewer'].pages and output_path:
            if messagebox.askokcancel("Proceed?", "Saving may overwrite some files in {0}".format(output_path)):
                self.clear_dir(self.output['browser'].path.get())
                self.copy_files(self.output['viewer'].pages, output_path, self.output['prefix'].prefix.get())
            else:
                print("no write")
        else:
            messagebox.showerror("Error", "No input/output directories selected")

    def merge_lists(self, a, b):
        return [j for i in itertools.zip_longest(a, b) for j in i if j]

    # Testing
    def clear_dir(self, path):
        for f in os.listdir(path):
            os.remove(path + os.sep + f)


# Start the GUI
root = tk.Tk()
PageZipper(root)

root.update()
root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
root.resizable(width=True, height=True)

# Ensure the icon works both from the python file, and the pyinstaller executable
icon_file = "icon.ico"
if not hasattr(sys, "frozen"):
    icon_file = os.path.join(os.path.dirname(__file__), icon_file)
else:
    icon_file = os.path.join(sys._MEIPASS, icon_file)
try:
    root.iconbitmap(default=icon_file)
except:
    print("Icon failed")
root.mainloop()
