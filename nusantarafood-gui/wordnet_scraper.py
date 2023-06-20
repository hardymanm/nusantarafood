import json
import re
import tkinter as tk
import types
from tkinter import messagebox
from urllib.parse import urljoin
import requests


# Custom text widget with scrollbar
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
    listbox = Listbox(*args, **kwargs)

    def get_selection(self):
        selected_index = listbox.curselection()
        if not selected_index:
            return None, None

        selected_item = listbox.get(selected_index[0])
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

def StackedLabels(*args, **kwargs):
    parent = args[0]

    labels = []
    for i, text in enumerate(args[1:]):
        widget = tk.Label(parent, text=text, anchor="nw", **kwargs)
        if i == 0:
            widget.pack(pady=(5, 0), fill="x")
        elif i == len(args[1:]) - 1:
            widget.pack(pady=(0, 5), fill="x")
        else:
            widget.pack(fill="x")

        labels.append(widget)

    return labels


class Api:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def get(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.get(url, auth=(self.username, self.password), **kwargs)

    def post(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.post(url, auth=(self.username, self.password), **kwargs)

    def patch(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.patch(url, auth=(self.username, self.password), **kwargs)

    def delete(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.delete(url, auth=(self.username, self.password), **kwargs)


# ------------------------------------------
# Utility Functions
# ------------------------------------------
def load_cfg(filename):
    with open(filename, 'r') as env_file:
        lines = env_file.read().splitlines()

    settings = dict()
    for line in lines:
        if line and line[0] != '#':
            key, value = line.split('=', 1)
            settings[key] = value

    return settings


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api = None
        self.settings = load_cfg('settings.cfg')

        self.title("NusantaraFood - Wordnet Scraper")
        self.geometry("1000x600")

        # ------------------------------------------
        # Top row (Login)
        # ------------------------------------------
        self.login_frame = tk.Frame(self, bg="#bbbbbb")
        self.login_frame.pack(fill='both')

        tk.Label(self.login_frame, text="Host", bg="#bbbbbb").grid(column=0, row=0, padx=(5, 5), pady=10)
        tk.Label(self.login_frame, text="Username", bg="#bbbbbb").grid(column=2, row=0, padx=(0, 5))
        tk.Label(self.login_frame, text="Password", bg="#bbbbbb").grid(column=4, row=0, padx=(0, 5))

        self.host_entry = Entry(self.login_frame, width=40, default=self.settings['host'])
        self.host_entry.grid(column=1, row=0, padx=(0, 10))

        self.username_entry = Entry(self.login_frame, width=20, default=self.settings['username'])
        self.username_entry.grid(column=3, row=0, padx=(0, 10))

        self.password_entry = Entry(self.login_frame, width=20, show="*", default=self.settings['password'])
        self.password_entry.grid(column=5, row=0, padx=(0, 10))

        self.login_button = tk.Button(self.login_frame, text="Login", pady=1, command=self.get_dataset_list)
        self.login_button.grid(column=6, row=0)

        # ------------------------------------------
        # 1st Column (Dataset List)
        # ------------------------------------------
        self.dataset_list_frame = tk.Frame(self, padx=5, pady=5, bg="#bbbbbb")
        self.dataset_list_frame.pack(side="left", fill="y")

        self.dataset_label = tk.Label(self.dataset_list_frame, text="Dataset List", anchor="nw", bg="#bbbbbb")
        self.dataset_label.pack(fill="x", pady=5)

        self.dataset_list_variable = tk.Variable(value=[])
        self.dataset_listbox = DbListbox(self.dataset_list_frame, self.dataset_list_variable, handle_select=self.handle_dataset_selected)

        # ------------------------------------------
        # 2nd Column (Dataset details)
        # ------------------------------------------
        self.dataset_detail_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        _, self.dataset_id_label = StackedLabels(self.dataset_detail_frame, "Dataset ID:", "-", bg="#cccccc", width=30)
        _, self.dataset_name_label = StackedLabels(self.dataset_detail_frame, "Dataset Name:", "-", bg="#cccccc", width=30)
        _, self.dataset_source_label = StackedLabels(self.dataset_detail_frame, "Source:", "-", bg="#cccccc", width=30)

        # ------------------------------------------
        # 3rd column Topics & Words from LDA
        # ------------------------------------------
        self.lda_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.lda_frame.pack(side="left", fill="y")

        tk.Label(self.lda_frame, text="LDA Terms", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.lda_terms_variable = tk.Variable(value=[])
        self.lda_terms_listbox = DbListbox(self.lda_frame, self.lda_terms_variable, width=30, height=25, handle_select=self.handle_term_selected)
        self.lda_terms_listbox.pack()

        self.delete_term_button = tk.Button(self.lda_frame, text="Delete term", command=self.handle_delete_term)

        # ------------------------------------------
        # 4th Column (Wiki details)
        # ------------------------------------------
        self.wordnet_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.wordnet_frame.pack(side="left", fill="both")

        tk.Label(self.wordnet_frame, text="Wordnet - Terms Hypernymn", anchor="nw", bg="#eeeeee").pack(pady=5, fill="x")

        self.wordnet_output_textbox = Textbox(self.wordnet_frame)
        self.wordnet_output_textbox.pack(fill="y", expand=True)

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

    def handle_delete_term(self):
        pass

    def handle_lda(self):
        pass

    def handle_scrape_wordnet(self):
        pass

    def handle_dataset_selected(self, event):
        dataset_id, dataset_name = self.dataset_listbox.get_selection()
        if not dataset_id:
            return

        # Update document list
        url = '/api/words/?dataset={}&fields=id,noun'.format(dataset_id)
        response = self.api.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        self.dataset_id_label.config(text=dataset_id)
        self.dataset_name_label.config(text=dataset_name)

        self.lda_terms_listbox.delete(0, 'end')
        for item in data:
            text = '#{} - {}'.format(item['id'], item['noun'])
            self.lda_terms_listbox.insert('end', text)

    def handle_term_selected(self, event):
        term_id, noun = self.lda_terms_listbox.get_selection()

        # Do nothing when document selection empty
        if not term_id:
            return

        # Update document list
        url = '/api/words/{}/'.format(term_id)
        response = self.api.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        output = ""
        hypernyms = json.loads(data['hypernym_json'])
        if hypernyms and len(hypernyms):
            for hypernym in hypernyms:
                output += f"{hypernym['name']}\n"
                output += "-"*len(hypernym['name'])
                output += f"\n{hypernym['definition']}\n\n\n"
        else:
            output = "No hypernym found in wordnet"

        self.wordnet_output_textbox.set_text(output)


if __name__ == "__main__":
    app = App()
    app.mainloop()
