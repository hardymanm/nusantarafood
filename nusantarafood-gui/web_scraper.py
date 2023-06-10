import tkinter as tk
from tkinter import messagebox
import requests
from urllib.parse import urljoin
import json
import re

# Custom text widget with scrollbar
class Textbox(tk.Frame):
    def __init__(self, parent, height=3):
        tk.Frame.__init__(self, parent)

        # Textbox for output
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")

        self.textbox = tk.Text(self, height=height)
        self.textbox.pack(side="left")

        self.textbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.textbox.yview)

    def get(self):
        return self.textbox.get('1.0', 'end-1c')

    def insert(self, *args, **kwargs):
        return self.textbox.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.textbox.delete(*args, **kwargs)


class Api:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def get(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.get(url, auth=(self.username, self.password), **kwargs)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api = None

        self.title("NusantaraFood - Web Scraper")
        self.geometry("1000x600")

        # Login
        self.login_frame = tk.Frame(self, bg="#bbbbbb")
        self.login_frame.pack(fill='both')

        tk.Label(self.login_frame, text="Host", bg="#bbbbbb").grid(column=0, row=0, padx=(5, 5), pady=10)
        tk.Label(self.login_frame, text="Username", bg="#bbbbbb").grid(column=2, row=0, padx=(0, 5))
        tk.Label(self.login_frame, text="Password", bg="#bbbbbb").grid(column=4, row=0, padx=(0, 5))

        self.host_entry = tk.Entry(self.login_frame, width=40)
        self.host_entry.insert(0, "http://localhost:8000")
        self.host_entry.grid(column=1, row=0, padx=(0, 10))

        self.username_entry = tk.Entry(self.login_frame, width=20)
        self.username_entry.insert(0, "admin")
        self.username_entry.grid(column=3, row=0, padx=(0, 10))

        self.password_entry = tk.Entry(self.login_frame, width=20, show="*")
        self.password_entry.insert(0, "nusantarafood")
        self.password_entry.grid(column=5, row=0, padx=(0, 10))

        self.login_button = tk.Button(self.login_frame, text="Login", pady=1, command=self.get_dataset_list)
        self.login_button.grid(column=6, row=0)

        # Dataset List Column
        self.dataset_list_frame = tk.Frame(self, padx=5, pady=5, bg="#bbbbbb")
        self.dataset_list_frame.pack(side="left", fill="y")

        self.dataset_label = tk.Label(self.dataset_list_frame, text="Dataset List", anchor="nw", bg="#bbbbbb")
        self.dataset_label.pack(fill="x", pady=5)

        self.dataset_list_variable = tk.Variable(value=[])
        self.dataset_listbox = self.add_listbox(self.dataset_list_frame, self.dataset_list_variable)
        self.dataset_listbox.bind('<<ListboxSelect>>', self.handle_dataset_selected)
        self.dataset_listbox.bind('<Down>', self.handle_dataset_selected)
        self.dataset_listbox.bind('<Up>', self.handle_dataset_selected)

        self.add_dataset_button = tk.Button(self.dataset_list_frame, text="Add Dataset", command=self.show_add_dataset_window)
        self.add_dataset_button.pack(anchor="nw", pady=5)

        # Dataset Detail Column
        self.dataset_detail_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        self.add_dataset_detail_label("Dataset Name")
        self.dataset_name_label = self.add_dataset_detail_value("-")
        self.add_dataset_detail_label("Source")
        self.dataset_source_label = self.add_dataset_detail_value("-")
        self.add_dataset_detail_label("Document Count")
        self.dataset_document_count_label = self.add_dataset_detail_value("-")

        # Document List Column
        self.document_list_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = self.add_listbox(self.document_list_frame, self.document_list_variable, width=25)
        self.document_listbox.bind('<<ListboxSelect>>', self.handle_document_selected)
        self.document_listbox.bind('<Down>', self.handle_document_selected)
        self.document_listbox.bind('<Up>', self.handle_document_selected)

        self.delete_document_button = tk.Button(self.document_list_frame, text="Delete Document", state="disabled")
        self.delete_document_button.pack(anchor="nw", pady=5)

        # Document Detail Column
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both")

        self.add_document_detail_label("Document Title")
        self.document_title_label = self.add_document_detail_value("-")
        self.add_document_detail_label("Document Title (Cleaned)")
        self.document_title_cleaned_label = self.add_document_detail_value("-")
        self.add_document_detail_label("Raw Content")
        self.document_raw_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_raw_content_textbox.pack(pady=(0, 5))

        self.add_document_detail_label("Selected Content")
        self.document_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_content_textbox.pack(pady=(0, 5))

        self.add_document_detail_label("Content Selector")
        self.add_textbox(self.document_detail_frame, height=1, pady=0)

        self.apply_selector_button = tk.Button(self.document_detail_frame, text="Apply", state='disabled')
        self.apply_selector_button.pack(anchor="nw", pady=5)

    def get_dataset_list(self):
        host = self.host_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.api = Api(host, username, password)
        try:
            response = self.api.get('/api/datasets/?fields=id,name')
        except requests.exceptions.ConnectionError:
            messagebox.showerror('Connection Error', 'Failed to connect to host')
            return

        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        self.dataset_listbox.delete(0, 'end')
        for item in data:
            text = '#{} - {}'.format(item['id'], item['name'])
            self.dataset_listbox.insert('end', text)

    @staticmethod
    def get_selected_listbox_item(listbox):
        selected_index = listbox.curselection()
        if not selected_index:
            return None, None

        selected_item = listbox.get(selected_index[0])
        matches = re.findall(r'^#(\d+) - (.+)$', selected_item)
        if len(matches) == 0:
            return None, None

        return matches[0]

    def handle_dataset_selected(self, event):
        dataset_id, dataset_name = self.get_selected_listbox_item(self.dataset_listbox)
        if not dataset_id:
            return

        # Update document list
        url = '/api/documents/?dataset={}&fields=id,title'.format(dataset_id)
        response = self.api.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        self.document_listbox.delete(0, 'end')
        for item in data:
            text = '#{} - {}'.format(item['id'], item['title'])
            self.document_listbox.insert('end', text)

        # Update dataset details
        self.dataset_name_label.config(text=dataset_name)
        self.dataset_document_count_label.config(text='{} items'.format(len(data)))

    def handle_document_selected(self, event):
        document_id, document_name = self.get_selected_listbox_item(self.document_listbox)

        if not document_id:
            return

        # Update document list
        url = '/api/documents/{}'.format(document_id)
        response = self.api.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        self.document_title_label.config(text=data['title'])
        self.document_title_cleaned_label.config(text=data['title_clean'])
        self.document_content_textbox.delete('1.0', 'end')
        self.document_content_textbox.insert('1.0', data['content'])

        if 'raw_content' in data:
            self.document_raw_content_textbox.delete('1.0', 'end')
            self.document_raw_content_textbox.insert('1.0', data['raw_content'])

    def add_dataset_detail_label(self, text, fg="#000000", pady=(5, 0)):
        widget = tk.Label(self.dataset_detail_frame, text=text, anchor="nw", bg="#cccccc", width=30, fg=fg)
        widget.pack(pady=pady, fill="x")
        return widget

    def add_dataset_detail_value(self, text):
        return self.add_dataset_detail_label(text, fg="#666666", pady=(0, 5))

    def add_document_detail_label(self, text, fg="#000000", pady=(5, 0)):
        widget = tk.Label(self.document_detail_frame, text=text, anchor="nw", bg="#eeeeee", width=35, fg=fg)
        widget.pack(pady=pady, fill="x")
        return widget

    def add_document_detail_value(self, text):
        return self.add_document_detail_label(text, fg="#666666", pady=(0, 5))

    @staticmethod
    def add_textbox(parent, height=8, pady=(0, 5)):
        widget = tk.Text(parent, height=height)
        widget.pack(pady=pady)
        return widget

    @staticmethod
    def add_listbox(parent, variable, width=25, height=25):
        # Frame to hold listbox and scrollbar
        listbox_frame = tk.Frame(parent, bg="#bbbbbb")
        listbox_frame.pack()

        # Listbox
        listbox = tk.Listbox(listbox_frame, width=width, height=height, listvariable=variable)
        listbox.pack(side="left")

        # scrollbar
        listbox_scroll = tk.Scrollbar(listbox_frame)
        listbox_scroll.pack(side="right", fill="y")

        listbox.config(yscrollcommand=listbox_scroll.set)
        listbox_scroll.config(command=listbox.yview)

        return listbox

    # Sub window
    def show_add_dataset_window(self):
        add_dataset_window = tk.Toplevel(self, padx=5, pady=5)
        add_dataset_window.attributes('-topmost', 'true')

        # Close window event
        # Handle button state in main window
        def handle_close():
            self.add_dataset_button['state'] = 'normal'
            add_dataset_window.destroy()

        add_dataset_window.protocol("WM_DELETE_WINDOW", handle_close)
        self.add_dataset_button['state'] = 'disabled'

        # Widgets
        def add_textbox(label, row):
            tk.Label(add_dataset_window, text=label).grid(column=0, row=row, sticky="w", pady=(0, 5), padx=(0, 10))
            widget = tk.Text(add_dataset_window, height=1, width=50, padx=5, pady=3)
            widget.grid(column=1, row=row, sticky="new", pady=(0, 5))
            return widget

        add_textbox("Dataset Name", 0)
        add_textbox("Max Num. of Document", 1)
        add_textbox("Starting Url", 2)

        tk.Label(add_dataset_window, text="Regex Rule").grid(column=0, row=3, sticky="nw", pady=(20, 5))
        add_textbox("Url", 4)
        add_textbox("Title", 5)
        add_textbox("Content", 6)

        start_button = tk.Button(add_dataset_window, text="Start Web Scraping")
        start_button.grid(column=1, row=7, sticky="nw", pady=(10, 20))

        tk.Label(add_dataset_window, text="Output").grid(column=0, row=8, sticky="wn", pady=(0, 5))

        # Textbox for output
        output_textbox = Textbox(add_dataset_window, height=10)
        output_textbox.grid(column=0, row=9, columnspan=2, sticky="news")


if __name__ == "__main__":
    app = App()
    app.mainloop()
