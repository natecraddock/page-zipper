import os
import tkinter as tk
from tkinter import ttk

from PIL import Image

import io

class Page:
    "A page object that contains the path to an image file, and the loaded thumbnail of that file"
    # TODO: Add thumbnail loading. This will allow the load_images function to tell if this file is a valid image or not
    def __init__(self, path):
        self.path = path
        self.size = (250, 250)
        self.selected = False
        self.thumb = self.make_thumbnail()

    def make_thumbnail(self):
        im = Image.open(self.path)
        im.thumbnail(self.size)
        b = io.BytesIO()
        im.save(b, 'gif')

        return tk.PhotoImage(data=b.getvalue())


class ImageFrame(tk.Frame):
    '''A frame that holds a canvas for loaded images. Can scroll horizontally'''
    def __init__(self, root, pages, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.pages = pages
        self.page_frames = []

        self.canvas = tk.Canvas(self, background='#FFFFFF', height=250)
        self.scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky='ew')
        self.scrollbar.grid(row=1, column=0, sticky='nesw')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.draw_pages()

        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_pages(self):
        for i, page in enumerate(self.pages):
            spacing = 20
            name = os.path.splitext(os.path.basename(page.path))[0]
            size = page.size[0]
            #size = 20

            # Create a frame for the image and text and save it to a list
            frame = self.canvas.create_rectangle((size * i) + (i * spacing), 0, (size * i) + (i * spacing) + size, size)
            self.canvas.create_image((size * i) + (size / 2) + (i * spacing), (size / 2), image=page.thumb, tags=str(i))
            self.canvas.create_text((size * i) + (size / 2) + (i * spacing), size, font=("tkdefaultfont", 10), text=name)

    def on_click(self, event):
        item = self.canvas.find_withtag('current')
        if self.canvas.type(item) == "image":
            self.canvas.gettags(item)
            print(self.pages[item])
            self.canvas.delete(item)


class Window:
    def __init__(self, root):
        self.root = root

        self.create_gui()


    def create_gui(self):
        self.root.title("Image Viewer")

        pages = self.load_pages('left')

        self.viewer = ImageFrame(self.root, pages)
        self.viewer.grid(row=0, column=0, sticky='nesw')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def load_pages(self, directory):
        paths = os.listdir(directory)
        paths.sort()

        return [Page(directory + os.sep + path) for path in paths]

root = tk.Tk()
Window(root)
root.mainloop()
