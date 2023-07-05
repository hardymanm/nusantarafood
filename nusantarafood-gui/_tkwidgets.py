import re
import tkinter as tk
import types


class Textbox(tk.Frame):
    def __init__(self, parent, height=3, **kwargs):
        tk.Frame.__init__(self, parent)

        # Textbox for output
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")

        self.textbox = tk.Text(self, height=height, **kwargs)
        self.textbox.pack(side="left", fill="both", expand=True)

        self.textbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.textbox.yview)

    def get(self):
        return self.textbox.get('1.0', 'end-1c')

    def insert(self, *args, **kwargs):
        self.textbox.insert(*args, **kwargs)

    def insert_end(self, *args, **kwargs):
        self.textbox.insert('end', *args, **kwargs)
        self.see('end')

    def delete(self, *args, **kwargs):
        return self.textbox.delete(*args, **kwargs)

    def see(self, *args, **kwargs):
        return self.textbox.see(*args, **kwargs)

    def set_text(self, text):
        self.textbox.delete('1.0', 'end')
        if text:
            self.textbox.insert('1.0', text)


def Listbox(parent, variable, width=25, height=25, handle_select=None, **kwargs):
    # Frame to hold listbox and scrollbar
    listbox_frame = tk.Frame(parent, bg="#bbbbbb")
    listbox_frame.pack()

    # Listbox
    listbox = tk.Listbox(listbox_frame, width=width, height=height, listvariable=variable, **kwargs)
    listbox.pack(side="left")

    # scrollbar
    listbox_scroll = tk.Scrollbar(listbox_frame)
    listbox_scroll.pack(side="right", fill="y")

    listbox.config(yscrollcommand=listbox_scroll.set)
    listbox_scroll.config(command=listbox.yview)

    if handle_select:
        listbox.bind('<<ListboxSelect>>', handle_select)
        listbox.bind('<Down>', handle_select)
        listbox.bind('<Up>', handle_select)

    return listbox


def DbListbox(*args, **kwargs):
    pattern = kwargs.pop('pattern') if 'pattern' in kwargs else None
    listbox = Listbox(*args, **kwargs)

    def get_selection(self):
        selected_index = listbox.curselection()
        if not selected_index:
            return None, None

        selected_item = listbox.get(selected_index[0])

        if pattern:
            matches = re.findall(pattern, selected_item)
        else:
            matches = re.findall(r'^#(\d+) - (.+)$', selected_item)

        if len(matches) == 0:
            return None, None

        return matches[0]

    listbox.get_selection = types.MethodType(get_selection, listbox)

    return listbox


def Entry(*args, default='', **kwargs):
    entry = tk.Entry(*args, **kwargs)
    entry.insert(0, default)
    return entry


def EntryRow(parent, text="", row=None, pady=(0, 5), **kwargs):
    tk.Label(parent, text=text).grid(column=0, row=row, sticky="w", pady=pady, padx=(0, 10))
    widget = Entry(parent, width=50, **kwargs)
    widget.grid(column=1, row=row, sticky="new", pady=pady)
    return widget


def StackedLabels(*args, **kwargs):
    parent = args[0]

    labels = []
    for i, text in enumerate(args[1:]):
        widget = tk.Label(parent, text=text, anchor="nw", justify="left", **kwargs)
        if i == 0:
            widget.pack(pady=(5, 0), fill="x")
        elif i == len(args[1:]) - 1:
            widget.pack(pady=(0, 10), fill="x")
        else:
            widget.pack(fill="x")

        labels.append(widget)

    return labels

