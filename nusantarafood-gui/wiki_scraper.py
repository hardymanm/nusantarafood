import json
import re
import threading
import tkinter as tk
import types
from tkinter import messagebox
from urllib.parse import urljoin
import wikipedia
import requests


# Custom text widget with scrollbar
class Textbox(tk.Frame):
    def __init__(self, parent, height=3, **kwargs):
        tk.Frame.__init__(self, parent)

        # Textbox for output
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")

        self.textbox = tk.Text(self, height=height, **kwargs)
        self.textbox.pack(side="left", fill="x", expand=True)

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
def scrape_wikipedia(title, lang):
    try:
        wikipedia.set_lang(lang)
        return wikipedia.summary(title, sentences=4)

    except wikipedia.PageError:
        print('Not found in {}.wikipedia'.format(lang))
        return ''


def extract_summary(summary, default_summary):
    pattern = r'(ialah|adalah|merupakan|merangkumi|kepada|makanan|consist |is a |consisting |made|is an )(.+?)[+,.;]'
    matches = re.findall(pattern, summary)
    regex_dot_matches = [match[1].strip() for match in matches]

    if len(regex_dot_matches) > 0:
        return ' '.join(regex_dot_matches)

    return default_summary


def get_wiki_summary(document_title, lang, default_summary):
    summary = scrape_wikipedia(document_title, lang)
    return extract_summary(summary, default_summary)


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

        self.title("NusantaraFood - Wiki Scraper")
        self.geometry("1000x720")

        # ------------------------------------------
        # Sub-window (Add dataset)
        # ------------------------------------------
        self.add_dataset_window = None
        self.clean_dataset_window = None

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
        _, self.dataset_document_count_label = StackedLabels(self.dataset_detail_frame, "Document Count:", "-", bg="#cccccc", width=30)

        self.scrape_wiki_button = tk.Button(self.dataset_detail_frame, text="Scrape Wiki", command=self.handle_scrape_wiki)
        self.scrape_wiki_button.pack(side="left", anchor="nw", pady=5)

        # ------------------------------------------
        # 3rd Column (Document list)
        # ------------------------------------------
        self.document_list_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = DbListbox(self.document_list_frame, self.document_list_variable, width=25, handle_select=self.handle_document_selected)

        # ------------------------------------------
        # 4th Column (Wiki details)
        # ------------------------------------------
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both")

        _, self.document_title_label = StackedLabels(self.document_detail_frame, "Document Title:", "-", bg="#eeeeee", width=35)
        _, self.document_title_cleaned_label = StackedLabels(self.document_detail_frame, "Document Title (Cleaned):", "-", bg="#eeeeee", width=35)

        tk.Label(self.document_detail_frame, text="Wiki ID", anchor="nw", bg="#eeeeee", width=35).pack( pady=(5, 0), fill="x")
        self.wiki_id_textbox = Textbox(self.document_detail_frame, height=4)
        self.wiki_id_textbox.pack(pady=(0, 5))

        tk.Label(self.document_detail_frame, text="Wiki MS", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.wiki_ms_textbox = Textbox(self.document_detail_frame, height=4)
        self.wiki_ms_textbox.pack(pady=(0, 5))

        tk.Label(self.document_detail_frame, text="Wiki EN", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.wiki_en_textbox = Textbox(self.document_detail_frame, height=4)
        self.wiki_en_textbox.pack(pady=(0, 5))

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

    def handle_scrape_wiki(self):
        def scrape():
            dataset_id = self.dataset_id_label["text"]
            self.scrape_wiki_button["state"] = "disabled"
            try:
                response = self.api.get(f"/api/documents/?dataset={dataset_id}&fields=id")
            except Exception:
                messagebox.showerror("Request Failed", f"GET request error /api/documents/?dataset={dataset_id}&fields=id")
                return

            if response.status_code not in (200, 201):
                # self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                # self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                # self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                return

            data = json.loads(response.text)
            for obj in data:
                try:
                    response = self.api.get(f"/api/documents/{obj['id']}/?fields=id,title,definition_id,definition_ms,definition_en")
                except Exception:
                    messagebox.showerror("Request Failed", f"GET request error /api/documents/{obj['id']}&fields=id,title,definition_id,definition_ms,definition_en")
                    continue

                if response.status_code not in (200, 201):
                    # self.output_textbox.insert_end(
                    #     '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    # self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                    # self.output_textbox.insert_end(
                    #     '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    return

                document = json.loads(response.text)
                title = document['title']
                wiki_id = get_wiki_summary(title, 'id', '')
                wiki_ms = get_wiki_summary(title, 'ms', '')
                wiki_en = get_wiki_summary(title, 'en', '')

                payload = {'definition_id': wiki_id, 'definition_ms': wiki_ms, 'definition_en': wiki_en}
                response = self.api.patch(f"/api/documents/{obj['id']}/", data=payload)
                if response.status_code not in (200, 201):
                    # self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    # self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                    # self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    return

                # self.window.event_generate("<<LogOutput>>", when="tail", state=f"'PATCH /api/documents/{obj['id']}/'")
                # self.output_textbox.insert_end(f"PATCH /api/documents/{obj['id']}/\n")
                print(f"PATCH /api/documents/{obj['id']}/")

            # self.output_textbox.insert_end("Clean finished\n")
            self.scrape_wiki_button["state"] = "normal"
            print(f"Scrape wiki finish")

        thread = threading.Thread(target=scrape, daemon=True)
        thread.start()

    def handle_dataset_selected(self, event):
        dataset_id, dataset_name = self.dataset_listbox.get_selection()
        if not dataset_id:
            return

        # Update document list
        url = '/api/documents/?dataset={}&fields=id,title,definition_id,definition_ms,definition_en'.format(dataset_id)
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
        self.dataset_id_label.config(text=dataset_id)
        self.dataset_name_label.config(text=dataset_name)
        self.dataset_document_count_label.config(text='{} items'.format(len(data)))

    def handle_document_selected(self, event):
        document_id, document_name = self.document_listbox.get_selection()

        # Do nothing when document selection empty
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

        if 'definition_id' in data:
            self.wiki_id_textbox.set_text(data['definition_id'])

        if 'definition_ms' in data:
            self.wiki_ms_textbox.set_text(data['definition_ms'])

        if 'definition_en' in data:
            self.wiki_en_textbox.set_text(data['definition_en'])


if __name__ == "__main__":
    app = App()
    app.mainloop()
