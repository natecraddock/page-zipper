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
        self.size = 100
        self.thumb = self.make_thumbnail()

    def make_thumbnail(self):
        im = Image.open(self.path)

        im.thumbnail((self.size, self.size))
        b = io.BytesIO()
        im.save(b, 'gif')
        return tk.PhotoImage(data=b.getvalue())


class PageGroup:
    '''An object that holds a group of pages'''
    def __init__(self, pages):
        self.pages = pages


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


class ImageFrame(tk.Frame):
    '''A frame that holds a canvas for loaded images. Can scroll horizontally'''
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.page_frames = []

        self.canvas = tk.Canvas(self, background='#FFFFFF', height=125, width=600)
        self.scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky='ew')
        self.scrollbar.grid(row=1, column=0, sticky='nesw')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        #self.draw_pages()

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_pages(self):
        # CLEAR ALL
        self.canvas.delete('all')

        for i, page in enumerate(self.pages):
            spacing = 20
            name = os.path.splitext(os.path.basename(page.path))[0]
            size = page.size

            # Create a frame for the image and text and save it to a list
            frame = self.canvas.create_rectangle((size * i) + (i * spacing), 0, (size * i) + (i * spacing) + size, size)
            self.canvas.create_image((size * i) + (size / 2) + (i * spacing), (size / 2), image=page.thumb, tags=str(i))
            self.canvas.create_text((size * i) + (size / 2) + (i * spacing), size, font=("tkdefaultfont", 10), text=name)

            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_click(self, event):
        item = self.canvas.find_withtag('current')
        if self.canvas.type(item) == "image":
            self.canvas.gettags(item)
            print(self.pages[item])
            self.canvas.delete(item)


class PageZipper:
    def __init__(self, root):
        self.root = root

        # Create dictionary variables for the three UI areas
        self.left = {'valid':False, 'pages':[]}
        self.right = {'valid':False, 'pages':[]}
        self.output = {'valid':False, 'pages':[]}

        self.create_gui()

    def create_gui(self):
        root.title("Page Zipper v0.2")

        # Disable tearing for the menubar
        root.option_add('*tearOff', 'FALSE')

        # Create Menu Bar
        self.menubar = tk.Menu(self.root)
        self.menu_file = tk.Menu(self.menubar)
        #self.menu_edit = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)

        self.menu_file.add_command(label='Exit', command=lambda : quit())

        self.menubar.add_cascade(menu=self.menu_file, label='File')
        #self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menubar.add_cascade(menu=self.menu_help, label='Help')

        self.root.config(menu=self.menubar)


        # Create the frames and separators to pack UI elements into
        self.left['frame'] = tk.Frame(self.root)
        self.left['frame'].grid(row=0, column=0, sticky='nesw')
        ttk.Separator(self.root, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=5)
        self.right['frame'] = tk.Frame(self.root)
        self.right['frame'].grid(row=2, column=0, sticky='nesw')
        ttk.Separator(self.root, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=5)
        self.output['frame'] = tk.Frame(self.root)
        self.output['frame'].grid(row=4, column=0, sticky='nesw')


        # Fill Left Pages Frame
        tk.Label(self.left['frame'], text="Left Pages").grid(row=0, column=0, sticky='nsw', padx=10, pady=10)
        self.left['browser'] = DirectoryBrowser(self.left['frame'], "Path:")
        self.left['pagesframe'] = ImageFrame(self.left['frame'])
        self.left['browser'].grid(row=1, column=0, sticky='nesw', padx=10)
        self.left['pagesframe'].grid(row=2, column=0, sticky='nesw', padx=10, pady=5)
        self.left['frame'].columnconfigure(0, weight=1)

        # Fill Right Pages Frame
        tk.Label(self.right['frame'], text="Right Pages").grid(row=0, column=0, sticky='nsw', padx=10, pady=10)
        self.right['browser'] = DirectoryBrowser(self.right['frame'], "Path:")
        self.right['pagesframe'] = ImageFrame(self.right['frame'])
        self.right['browser'].grid(row=1, column=0, sticky='nesw', padx=10)
        self.right['pagesframe'].grid(row=2, column=0, sticky='nesw', padx=10, pady=5)
        self.right['frame'].columnconfigure(0, weight=1)

        # Create Output Frame
        tk.Label(self.output['frame'], text="Output").grid(row=0, column=0, sticky='nsw', padx=10, pady=10)
        self.output['browser'] = DirectoryBrowser(self.output['frame'], "Path:")
        self.save_button = tk.Button(self.output['frame'], text="Save", command=self.save_files)
        self.output['browser'].grid(row=1, column=0, sticky='nesw', padx=10)
        self.save_button.grid(row=2, column=0, sticky='ew')
        self.output['frame'].columnconfigure(0, weight=1)

        # For horizontal expanding of all widgets
        self.root.columnconfigure(0, weight=1)

        # Set callbacks to load images that are called when path is valid
        self.left['browser'].callback = lambda area=self.left : self.on_input(area)
        self.right['browser'].callback = lambda area=self.right : self.on_input(area)


    # Create a toplevel widget that displays a progressbar as the pages are loaded
    def load_pages(self, directory):
        paths = os.listdir(directory)
        paths.sort()

        top = tk.Toplevel()
        top.title("Loading Pages")
        tk.Label(top, text="Loading Pages").grid(row=0, column=0, sticky='w', padx=10, pady=20)
        progress = ttk.Progressbar(top, orient='horizontal', length=200, mode='determinate', maximum=100)
        progress.grid(row=1, column=0, sticky='ew', padx=5)

        step = float(100.0/len(paths))

        temp = []
        progress['value'] = 0
        for path in paths:
            temp.append(Page(os.path.join(directory, path)))
            progress['value'] += step

        return temp

    def on_input(self, area):
        path = area['browser'].path.get()

        # Load pages, then draw in ImageViewer
        area['pages'] = self.load_pages(path)

        if area['pages']:
            area['pagesframe'].pages = area['pages']
            area['pagesframe'].draw_pages()

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
