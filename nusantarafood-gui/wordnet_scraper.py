import json
import threading
import tkinter as tk
from tkinter import messagebox, font
import requests
from imports.ui import *
from imports.client import Api
from imports.utils import *

import imports.lda as lda


class ScrapeWordnetWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.scrape_wordnet_button['state'] = 'disabled'
        self.dataset_id, self.dataset_name = self.parent.dataset_listbox.get_selection()

        self.window = tk.Toplevel(parent, padx=5, pady=5)
        self.window.title("Scrape Wordnet")
        self.window.protocol("WM_DELETE_WINDOW", self.handle_close)

        lda_label = tk.Label(self.window, text="LDA Model")
        lda_label.grid(column=0, row=0, sticky="nw", pady=(0, 5))
        f = font.Font(lda_label, lda_label.cget("font"))
        f.configure(underline=True)
        lda_label.configure(font=f)

        self.passes_count_entry = EntryRow(self.window, "LDA Iteration", 1, default='20')
        # @TODO: topic count must be greater than 1. otherwise pyldavis will throw assertion error.
        #        no problem with lda_model
        self.topic_count_entry = EntryRow(self.window, "Topic count", 2, default='5')
        self.term_limit_entry = EntryRow(self.window, "Terms count per topic", 3, default='30')

        wordnet_label = tk.Label(self.window, text="Wordnet")
        wordnet_label.grid(column=0, row=4, sticky="nw", pady=(20, 5))
        wordnet_label.configure(font=f)
        self.language_entry = EntryRow(self.window, "Language", 5, pady=(0, 20), default='zsm')

        self.scrape_button = tk.Button(self.window, text="Scrape", command=self.handle_scrape)
        self.scrape_button.grid(column=1, row=6, sticky="nw", pady=(0, 10))

    def handle_close(self):
        self.parent.scrape_wordnet_button['state'] = 'normal'
        self.window.destroy()

    def handle_scrape(self):
        def task():
            self.scrape_button['state'] = 'disabled'
            if not self.dataset_id:
                return

            url = '/api/documents/?dataset={}&fields=id,content'.format(self.dataset_id)
            response = self.parent.api.get(url)
            data = json.loads(response.text)
            if response.status_code != 200:
                messagebox.showerror('error', data['detail'])
                return

            contents = [document['content'] for document in data]

            num_topics = int(self.topic_count_entry.get())
            passes_count = int(self.passes_count_entry.get())
            num_terms = int(self.term_limit_entry.get())
            lang = self.language_entry.get()

            self.scrape_button.config(text="Running LDA...")

            # LDA model
            lda_model, lda_data = lda.make_LDAmodel(contents, num_topics, passes_count)
            payload = {"num_topics": num_topics, "passes": passes_count, "lda_data": lda_data.to_json()}
            self.parent.api.patch(f'/api/datasets/{self.dataset_id}/', data=payload)

            # Wordnet terms
            word_list = lda.get_word_list(lda_model, num_terms)
            word_list_with_hypernyms = [lda.scrape_hypernym(word, lang) for word in word_list]

            n = len(word_list_with_hypernyms)
            for i, (word, hypernyms) in enumerate(word_list_with_hypernyms):
                hypernym_json = json.dumps(hypernyms)
                payload = {"dataset": self.dataset_id, "noun": word, "hypernym_json": hypernym_json}
                self.parent.api.post('/api/words/', data=payload)

                self.scrape_button.config(text="Update db record {}/{}".format(i + 1, n))

            self.scrape_button.config(text="Finished")

        thread = threading.Thread(target=task, daemon=True)
        thread.start()


class App(WindowSizeMixin):
    def __init__(self):
        super().__init__()
        self.api = None
        self.settings = load_cfg('settings.cfg')

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

        self.scrape_wordnet_button = tk.Button(self.dataset_detail_frame, text="Scrape Wordnet", command=self.handle_scrape_wordnet)
        self.scrape_wordnet_button.pack(anchor="nw")

        # ------------------------------------------
        # 3rd column (LDA terms list)
        # ------------------------------------------
        self.lda_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.lda_frame.pack(side="left", fill="y")

        tk.Label(self.lda_frame, text="LDA Terms", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.lda_terms_variable = tk.Variable(value=[])
        self.lda_terms_listbox = DbListbox(self.lda_frame, self.lda_terms_variable, width=30, height=25, handle_select=self.handle_term_selected)
        self.lda_terms_listbox.pack()

        self.delete_term_button = tk.Button(self.lda_frame, text="Delete term", command=self.handle_delete_term)
        self.delete_term_button.pack(anchor="nw")

        # ------------------------------------------
        # 4th Column (Hypernyms)
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
        term_id, term_name = self.lda_terms_listbox.get_selection()
        if not term_id:
            return

        response = self.api.delete('/api/words/{}'.format(term_id))

        # Update term list
        index = self.lda_terms_listbox.curselection()
        self.lda_terms_listbox.delete(index)

    def handle_scrape_wordnet(self):
        ScrapeWordnetWindow(self)

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
