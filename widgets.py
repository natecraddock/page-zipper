import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font

import os
import utils

import zipper


class LabeledEntry(tk.Frame):
    '''A tkinter widget for a labeled entry'''
    def __init__(self, parent, label="Entry:"):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text=label).grid(row=0, column=0, sticky='nse')
        tk.Entry(self, textvariable=self.entry).grid(row=0, column=1, sticky='nsew', padx=5)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

    def set(self, value):
        self.entry.set(value)

    def get(self):
        return self.entry.get()


class LabeledIntEntry(LabeledEntry):
    def __init__(self, parent, label="Entry:"):
        self.entry = tk.IntVar()
        LabeledEntry.__init__(self, parent, label)


class LabeledStringEntry(LabeledEntry):
    def __init__(self, parent, label="Entry:"):
        self.entry = tk.StringVar()
        LabeledEntry.__init__(self, parent, label)


class DirectoryBrowser(tk.Frame):
    '''A tkinter widget for a labeled directory browser'''
    def __init__(self, parent, label="Choose Folder:", callback=lambda: None):
        tk.Frame.__init__(self, parent)

        self.callback = callback

        # Create GUI Elements for the Directory Browser Widget
        self.path = LabeledStringEntry(self, label=label)
        self.path.grid(row=0, column=0, sticky='nsew')
        tk.Button(self, text="Browse", command=self.browse).grid(row=0, column=1, sticky='nsw')

        # Weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

    def browse(self):
        if os.path.exists(self.path.get()):
            directory = filedialog.askdirectory(initialdir=self.path.get())
        else:
            directory = filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            if os.path.exists(directory):
                self.path.set(directory)
                self.callback()


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


# TODO: Add option to set prefix on the rename
class PrefixEntry(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.prefix = LabeledStringEntry(self, label="File Prefix:")
        self.prefix.grid(row=0, column=1, sticky='nsew', padx=5)
        self.prefix.set("img_")


class OutputFrame(tk.Frame):
    '''A frame for a thumbnail viewer and browser'''
    def __init__(self, root, callback=lambda: None):
        self.pages = []

        tk.Frame.__init__(self, root)
        self.viewer = ThumbnailViewer(self, group=False)
        self.browser = DirectoryBrowser(self, "Output Path:")
        self.prefix = PrefixEntry(self)
        self.save_button = tk.Button(self, text="Save", command=callback)

        self.viewer.grid(row=0, column=0, sticky='nesw', padx=10, pady=5)
        self.browser.grid(row=1, column=0, sticky='nesw', padx=10)
        self.prefix.grid(row=2, column=0, sticky='nsw', padx=10, pady=5)
        self.save_button.grid(row=3, column=0, sticky='', pady=5)

        self.columnconfigure(0, weight=1)


class PagesFrame(tk.Frame):
    '''A frame for a thumbnail viewer and browser'''
    def __init__(self, root, label, callback=lambda: None):
        self.pages = []
        self.callback = callback

        tk.Frame.__init__(self, root)
        tk.Label(self, text=label).grid(row=0, column=0, sticky='w', padx=5, pady=5, columnspan=2)
        self.browser = DirectoryBrowser(self, "")
        self.viewer = ThumbnailViewer(self, group=True, callback=self.on_viewer_update)

        self.browser.grid(row=1, column=0, sticky='nesw', padx=10)
        self.viewer.grid(row=2, column=0, sticky='nesw', padx=10, pady=5)

        self.columnconfigure(0, weight=1)

        self.browser.callback = self.on_input

    # Create a widget that displays a progressbar as the pages are loaded
    def load_pages(self, directory):
        paths = os.listdir(directory)
        paths.sort()

        if len(paths) > 0:
            progress = ProgressPopup("Loading Pages", len(paths))
            temp = []
            for path in paths:
                if not os.path.isdir(os.path.join(directory, path)):
                    p = utils.Page(os.path.join(directory, path))

                    if p.thumb is not None:
                        temp.append(p)
                    progress.next()
                    progress.log_message("Created thumbnail for {}".format(path))

            progress.destroy()

            return temp
        else:
            print("No images found")

    def on_input(self):
        path = self.browser.path.get()

        # Load pages, then draw in ImageViewer
        self.pages = self.load_pages(path)

        if self.pages:
            self.viewer.reload_pages(self.pages)

    def on_viewer_update(self):
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
        self.use_groups = group

        self.canvas = tk.Canvas(self, background='#FFFFFF', height=int(utils.Page.size * 0.85), width=800)
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
            size = utils.Page.size
            n = str(i + 1).zfill(len(str(len(self.pages))))

            # Create a frame for the image and text and save it to a list
            box = (size * i) + (i * spacing), 1, (size * i) + (i * spacing) + size, utils.Page.size + 25
            if i in self.selected:
                self.canvas.create_rectangle(box, fill='lightblue', outline='', tags="background")

            if type(page) is utils.Page:
                name = n + "  " + page.name
                self.canvas.create_image((size * i) + (i * spacing), spacing / 2, image=page.thumb, anchor="nw")
                self.canvas.create_text((size * i) + (i * spacing) + (size / 2), int(size * 0.75), font=("tkdefaultfont", 10), text=name, anchor="n")
            elif type(page) is utils.PageGroup:
                # Draw first page of the group
                self.canvas.create_image((size * i) + (i * spacing), spacing / 2, image=page.pages[0].thumb, anchor="nw")
                self.canvas.create_text((size * i) + (i * spacing) + (size / 2), int(size * 0.75), font=("tkdefaultfont", 10), text=n + " " + page.name)

            self.hit_boxes.append(self.canvas.create_rectangle(box, fill='', outline='', tags="hitbox"))

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.scrollbar.set(self.scroll_location[0], self.scroll_location[1])

    def on_click(self, event):
        if self.use_groups:
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

            group = utils.PageGroup([self.pages.pop(first_index) for i in reversed(self.selected)])

            # Replace the grouped pages with the page group
            self.pages.insert(first_index, group)
            self.update()
        else:
            messagebox.showerror("Error", "No images are selected")

    def ungroup(self):
        if self.selected:
            temp = []
            for p in self.pages:
                if type(p) is utils.PageGroup and self.pages.index(p) in self.selected:
                    temp.extend(p.pages)
                else:
                    temp.append(p)

            self.pages = temp[:]
            self.update()
        else:
            messagebox.showerror("Error", "No page groups are selected")
