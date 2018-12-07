import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import sys
import os
import webbrowser

import widgets
import utils
import zipper


class HelpFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        tk.Label(parent, text="Page Zipper v1.1", font=("tkdefaultfont", 18)).grid(row=0, pady=10)

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


class RenameFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.browser = widgets.DirectoryBrowser(self, "Rename files in folder:")
        self.browser.grid(row=0, column=0, sticky='nesw', padx=5, columnspan=2)

        self.number = widgets.LabeledIntEntry(self, label="Starting Number:")
        self.number.grid(row=1, column=0, sticky='nsw')
        self.number.set(1)
        
        self.prefix = widgets.PrefixEntry(self)
        self.prefix.grid(row=2, column=0, sticky='nsw')

        self.rename_button = tk.Button(self, text='Rename Files', command=self.rename)
        self.rename_button.grid(row=3, column=0, columnspan=2, sticky='nesw', padx=5)

    def rename(self):
        if os.path.exists(self.browser.path.get()):
            utils.rename_files(self.browser.path.get(), self.number.get(), self.prefix.prefix.get())
        else:
            messagebox.showerror("Error", "No directory specified, or path is invalid")


class PageZipperWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Zipper v1.1")

        # Create dictionary variables for the three UI areas
        self.left = {'valid':False, 'pages':[]}
        self.right = {'valid':False, 'pages':[]}
        self.utils = {}
        self.output = {'valid':False, 'pages':[]}

        self.create_gui()

    def create_gui(self):
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

        # Add Help Frame
        HelpFrame(self.help_tab).grid(row=0, column=0, sticky='nesw')

        # Create Frames for each area
        self.left_frame = widgets.PagesFrame(self.input_tab, "Left", self.on_viewer_update)
        self.right_frame = widgets.PagesFrame(self.input_tab, "Right", self.on_viewer_update)
        self.output_frame = widgets.OutputFrame(self.output_tab, self.save_files)
        self.utils_frame = tk.Frame(self.utils_tab)

        # Align to grid
        self.left_frame.grid(row=0, column=0, sticky='nesw', pady=15)
        ttk.Separator(self.input_tab, orient='horizontal').grid(row=1, column=1, sticky='ew')
        self.right_frame.grid(row=2, column=0, sticky='nesw', pady=15)
        self.output_frame.grid(row=0, column=0, sticky='nesw', padx=5)
        self.utils_frame.grid(row=0, column=0, sticky='nsew', pady=15)

        # Make each frame expand
        self.left_frame.columnconfigure(0, weight=1)
        self.right_frame.columnconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)
        self.utils_frame.columnconfigure(0, weight=1)

        # Populate the Uilities Tab
        self.renamer = RenameFrame(self.utils_frame)
        self.renamer.grid(row=0, column=0, sticky='nsew')
        self.renamer.columnconfigure(0, weight=1)

        # For horizontal expanding of all widgets
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)
        self.input_tab.columnconfigure(0, weight=1)
        self.output_tab.columnconfigure(0, weight=1)
        self.help_tab.columnconfigure(0, weight=1)
        self.utils_tab.columnconfigure(0, weight=1)

    def on_viewer_update(self):
        merged = zipper.merge_lists(self.right_frame.viewer.pages, self.left_frame.viewer.pages)
        merged = zipper.ungroup(merged)

        self.output_frame.viewer.reload_pages(merged)

    def save_files(self):
        output_path = self.output_frame.browser.path.get()
        if self.left_frame.viewer.pages and self.right_frame.viewer.pages and output_path:
            if messagebox.askokcancel("Proceed?", "Saving may overwrite some files in {0}".format(output_path)):
                zipper.clear_dir(self.output_frame.browser.path.get())
                zipper.copy_files(self.output_frame.viewer.pages, output_path, self.output_frame.prefix.prefix.get())
            else:
                print("no write")
        else:
            messagebox.showerror("Error", "No input/output directories selected")


def create_window():
    root = tk.Tk()
    PageZipperWindow(root)

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
