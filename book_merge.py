# Book Merge v0.2
# Elder Nathan Craddock 2018

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import imghdr

import os
import shutil

class Page:
    def __init__(self, path):
        self.path = path
        
        # Add thumbnail loading v0.3
        

class DirectoryFrame(tk.Frame):
    def __init__(self, parent, title="Output Frame:", label="Label:", entry="", button_text="Browse"):
        tk.Frame.__init__(self, parent)
        
        # Images
        self.images = ""
        
        self.title = tk.Label(self, text=title)
        self.browser = DirBrowse(self, label, entry, button_text)
        self.info_label = tk.Label(self, text="")

        self.title.grid(row=0, column=0, sticky='nsw', padx=10)
        self.browser.grid(row=1, column=0, sticky='nesw', padx=10)
        self.info_label.grid(row=2, column=0, sticky='nsw', padx=10)
        
        self.columnconfigure(0, weight=1)
        
        # Add callback for path modification
        self.browser.path.trace('w', self.validate_input)
        
        self.validate_input()
    
    # TODO: single line this?
    def load_images(self, dir):
        paths = []
        # Use os.scandir()?
        for path in os.listdir(dir):
            if imghdr.what(dir + os.sep + path): # If image
                paths.append(dir + os.sep + path)
        return paths
    
    # TODO: create Page objects in load_images, then check for page.path
    def validate_input(self, *dummy):
        path = self.browser.path.get()
        if path == "":
            self.info_label['text'] = "Select a path"
        else:
            # Check if path is real
            if os.path.exists(path):
                # Scan for images
                self.images = self.load_images(path)
                if self.images:
                    self.info_label['text'] = "Found " + str(len(self.images)) + " images"
                else:
                    self.info_label['text'] = "No images found"
                
            else:
                self.info_label['text'] = "Invalid path"
        

class PagesFrame(DirectoryFrame):
    def __init__(self, parent, title="Pages Frame:", label="Label:", entry="", button_text="Browse"):
        DirectoryFrame.__init__(self, parent, title, label, entry, button_text)        


class OutputFrame(DirectoryFrame):
    def __init__(self, parent, title="Output Frame:", label="Label:", entry="", button_text="Browse"):
        DirectoryFrame.__init__(self, parent, title, label, entry, button_text)
        
        self.write_button = tk.Button(self, text="Write")
        self.write_button.grid(row=3, column=0)
        

class DirBrowse(tk.Frame):
    def __init__(self, parent, label="Label:", entry="", button_text="Browse"):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        # Variable to access the entry text
        self.path = tk.StringVar()
        
        self.label = tk.Label(self, text=label)
        self.entry = tk.Entry(self, textvariable=self.path)
        self.button = tk.Button(self, text=button_text)
        self.button['command'] = self.get_path
        
        # Grid
        self.label.grid(column=0, row=0, sticky='nse')
        self.entry.grid(column=1, row=0, sticky='nsew', padx=5)
        self.button.grid(column=2, row=0, sticky='nse')
        
        # Weights
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=0)
        
    def get_path(self):
        directory = filedialog.askdirectory(initialdir=os.getcwd())
        if directory:
            self.path.set(directory)
        

class PageZipper:
    def __init__(self, root):
        self.root = root
        
        self.create_gui()
        
    def create_gui(self):
        root.title("Page Zipper v0.2")
        
        # Disable tearing off the menubar
        #root.option_add('*tearOff', 'FALSE')
        
               
        # Create Menu Bar
        self.menubar = tk.Menu(self.root)
        self.menu_file = tk.Menu(self.menubar)
        self.menu_edit = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)
        
        self.menu_file.add_command(label='Exit', command=self.on_quit)
        
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menubar.add_cascade(menu=self.menu_help, label='Help')
        
        self.root.config(menu=self.menubar)
        
        
        self.left_pages_frame = PagesFrame(self.root, "Left Pages", "Path:", "", "Browse")
        self.left_pages_frame.grid(row=0, column=0, sticky='nesw')
        
        ttk.Separator(self.root, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=10)
        
        self.right_pages_frame = PagesFrame(self.root, "Right Pages", "Path:", "", "Browse")
        self.right_pages_frame.grid(row=2, column=0, sticky='nesw')
        
        ttk.Separator(self.root, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=10)
        
        self.output_frame = OutputFrame(self.root, "Output", "Path:", "", "Browse")
        self.output_frame.grid(row=4, column=0, sticky='nesw')     

        self.root.columnconfigure(0, weight=1)
        
        self.output_frame.write_button['command'] = self.write_files
        
        self.text = tk.Label(self.root, text="testing 1.. 2.. 3..")
        self.text.grid(row=5, column=0)
        
    def on_quit(self):
        quit()
        
    def copy_files(self, files, out, pre="img_"):
        for i in range(len(files)):
            new_file = pre + str(str(i + 1).zfill(len(str(len(files) + 1))) + os.path.splitext(files[i])[1]) #SUPER GROSS
            print(new_file)
            new_path = os.path.join(out, new_file)
            shutil.copy2(files[i], new_path)
            print("Created file", new_path)
        
    def write_files(self):
        print('TESTING: Clear output')
        self.clear_dir(self.output_frame.browser.path.get())
        
        print("MERGING PAGE LISTS")
        merged = self.merge_lists(self.right_pages_frame.images, self.left_pages_frame.images)
        
        print("COPYING FILES")
        
        self.copy_files(merged, self.output_frame.browser.path.get())
        
        
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
root.minsize(root.winfo_width() + 250, root.winfo_reqheight())
root.resizable(width=True, height=False)

root.mainloop()
