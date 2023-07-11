import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox, filedialog, font as tkFont
from imports.utils import *
from imports.ui import *
from imports.client import Api
import requests
from urllib.parse import urljoin, urldefrag
import json
import re
import hashlib
import os
from bs4 import BeautifulSoup

from imports.utils import is_absolute
from imports.utils import create_dir


def RuleRadioInputRow(parent, label, row):
    widget = EntryRow(parent, label, row)

    frame = tk.Frame(parent)
    frame.grid(column=1, row=row + 1, sticky="new", pady=(0, 5))
    var = tk.StringVar(value="split")
    split_comma_option = tk.Radiobutton(frame, variable=var, value="split", text="split comma")
    split_comma_option.pack(side="left")
    re_match_option = tk.Radiobutton(frame, variable=var, value="re.match", text="re.match")
    re_match_option.pack(side="left")
    re_search_option = tk.Radiobutton(frame, variable=var, value="re.search", text="re.search")
    re_search_option.pack(side="left")

    return widget, var


# ------------------------------------------
# Utility Functions
# ------------------------------------------
def get_cached_or_download(url):
    url_sha1 = hashlib.sha1(url.encode())
    filename = "downloads/{}.html".format(url_sha1.hexdigest())
    if os.path.exists(filename):
        with open(filename, "r") as f:
            print(f"Loaded from file {filename}")
            return f.read()
    else:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Downloaded {filename} from url {url}")
            with open(filename, "w") as f:
                f.write(response.text)

            return response.text

    print(f"Failed to get {url}")
    return None


def test_text(text, rule, option):
    result = False
    if not rule:
        return True

    if option == 'split':
        match = True
        for kw in rule.split(','):
            if kw not in text.lower():
                match = False
        if match:
            result = True
    elif option == 're.match':
        if re.match(rule, text):
            result = True
    elif option == 're.search':
        if re.search(rule, text, re.MULTILINE):
            result = True

    return result


def load_stopwords(filename):
    with open(filename, "r") as f:
        words = f.read().splitlines()

    return words


def to_batched_list(stopwords):
    import math

    batch_size = 50
    batches = []
    i = 0
    for x in range(math.ceil(len(stopwords)/batch_size)):
        batches.append(stopwords[i:i+batch_size])
        i += batch_size

    return batches


def remove_stopwords(text, stopwords):
    batches = to_batched_list(stopwords)

    for words in batches:
        pattern = r"\b({})\b".format("|".join(words))
        text = re.sub(pattern, "", text)

    return text


# ------------------------------------------
# Clean Document Window
# ------------------------------------------
class CleanDatasetWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.clean_dataset_button['state'] = 'disabled'

        self.stopword_filename = "stopwords.txt"

        # ------------------------------------------
        # UI Construct
        # ------------------------------------------
        self.window = tk.Toplevel(parent, padx=5, pady=5)
        self.window.title("Clean Dataset")
        self.window.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.window.geometry("640x480")

        # Clean options
        def checkbutton(text, default=True):
            var = tk.BooleanVar(value=True)
            widget = tk.Checkbutton(self.window, text=text, variable=var, onvalue=True, offvalue=False)
            if default:
                widget.select()
            widget.pack(anchor="nw")
            return widget, var

        tk.Label(self.window, text="Clean dataset's documents").pack(anchor="nw")

        self.clean_what_var = tk.StringVar(value="both")
        radio_frame = tk.Frame(self.window)
        radio_frame.pack(pady=(5, 20), anchor="nw")
        tk.Radiobutton(radio_frame, variable=self.clean_what_var, value="title", text="Title only").pack(side="left")
        tk.Radiobutton(radio_frame, variable=self.clean_what_var, value="body", text="Body only").pack(side="left")
        tk.Radiobutton(radio_frame, variable=self.clean_what_var, value="both", text="Both").pack(side="left")

        tk.Label(self.window, text="Operations").pack(anchor="nw", pady=(0, 5))
        _, self.remove_multi_space_var = checkbutton("Remove multiple spaces")
        _, self.remove_newline_var = checkbutton("Remove newlines")
        _, self.remove_long_sentence_var = checkbutton("Remove long sentences (content only)")
        _, self.remove_stopwords_var = checkbutton("Remove stopwords")

        tk.Label(self.window, text="Stopwords").pack(anchor="nw", pady=(20, 5))
        stopword_frame = tk.Frame(self.window)
        stopword_frame.pack(anchor="nw", pady=(0, 20))
        self.change_stopword_button = tk.Button(stopword_frame, text="Choose file", command=self.handle_choose_file)
        self.change_stopword_button.pack(side="left", padx=(0, 10))
        self.stopword_label = tk.Label(stopword_frame, text="stopwords.txt")
        self.stopword_label.pack(side="left")

        self.clean_button = tk.Button(self.window, text="Clean", command=self.handle_clean)
        self.clean_button.pack(anchor="nw", pady=(0, 20))

        self.output_textbox = Textbox(self.window, height=8, font=('DejaVu Sans Mono', 9, 'normal'), bg='black', fg='white')
        self.output_textbox.pack(fill="both", expand=True)

    def handle_close(self):
        self.parent.clean_dataset_button['state'] = 'normal'
        self.window.destroy()

    def handle_choose_file(self):
        self.stopword_filename = filedialog.askopenfilename()

        if not self.stopword_filename:
            self.stopword_filename = "stopwords.txt"

        self.stopword_label.config(text=self.stopword_filename)

    def handle_clean(self):
        def clean():
            dataset_id = self.parent.dataset_id_label["text"]

            try:
                response = self.parent.api.get(f"/api/documents/?dataset={dataset_id}&fields=id")
            except Exception:
                messagebox.showerror("Request Failed", f"GET request error /api/documents/?dataset={dataset_id}&fields=id")
                return

            if response.status_code not in (200, 201):
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                return

            data = json.loads(response.text)
            stopwords = load_stopwords(self.stopword_filename)
            for obj in data:
                try:
                    response = self.parent.api.get(f"/api/documents/{obj['id']}/?fields=title,raw_content")
                except Exception:
                    messagebox.showerror("Request Failed", f"GET request error /api/documents/{obj['id']}&fields=title,raw_content")
                    continue

                if response.status_code not in (200, 201):
                    self.output_textbox.insert_end(
                        '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                    self.output_textbox.insert_end(
                        '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    return

                document = json.loads(response.text)
                title = document['title']
                content = document['raw_content']

                if self.remove_long_sentence_var.get():
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "content":
                        sentences = content.split(".")
                        short_sentences = []
                        for sentence in sentences:
                            words = re.findall(r"\w+", sentence)
                            if len(words) <= 20:
                                short_sentences.append(sentence)
                        content = ".".join(short_sentences)

                if self.remove_stopwords_var.get():
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "title":
                        title = remove_stopwords(title, stopwords)
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "content":
                        content = remove_stopwords(content, stopwords)

                # Replace with ". " to make sure sentences not mixed up.
                if self.remove_newline_var.get():
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "title":
                        title = re.sub(r"\.?(\r\n|\n)+", ". ", title)
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "content":
                        content = re.sub(r"\.?(\r\n|\n)+", ". ", content)

                if self.remove_multi_space_var.get():
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "title":
                        title = re.sub(r" +", " ", title)
                    if self.clean_what_var.get() == "both" or self.clean_what_var.get() == "content":
                        content = re.sub(r" +", " ", content)

                payload = {'title_clean': title, 'content': content}
                response = self.parent.api.patch(f"/api/documents/{obj['id']}/", data=payload)
                if response.status_code not in (200, 201):
                    self.output_textbox.insert_end(
                        '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                    self.output_textbox.insert_end(
                        '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    return

                self.output_textbox.insert_end(f"PATCH /api/documents/{obj['id']}/\n")

            self.output_textbox.insert_end("Clean finished\n")

        thread = threading.Thread(target=clean, daemon=True)
        thread.start()


# ------------------------------------------
# Add Dataset Window
# ------------------------------------------
class AddDatasetWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.add_dataset_button['state'] = 'disabled'

        # ------------------------------------------
        # Web Scraping variables
        # ------------------------------------------
        self.url_downloaded = []
        self.url_queue = []
        self.url_queue_lock = threading.Lock()
        self.scraping_lock = threading.Lock()
        self.matched_document = []
        self.document_count = 0

        # ------------------------------------------
        # UI Construct
        # ------------------------------------------
        self.window = tk.Toplevel(parent, padx=5, pady=5)
        self.window.protocol("WM_DELETE_WINDOW", self.handle_close)
        # self.window.attributes('-topmost', 'true')

        # Scraping Input
        self.dataset_name_entry = EntryRow(self.window, "Dataset Name", 0)
        self.max_document_count_entry = EntryRow(self.window, "Max Num. of Document", 1)
        self.start_url_entry = EntryRow(self.window, "Starting Url", 2)

        # -- Rules
        tk.Label(self.window, text="Rules").grid(column=0, row=3, sticky="nw", pady=(20, 5))

        self.url_contains_entry, self.url_option = RuleRadioInputRow(self.window, "Url contains", 4)
        self.url_not_contains_entry, self.url_not_option = RuleRadioInputRow(self.window, "Url not contains", 6)
        self.title_contains_entry, self.title_option = RuleRadioInputRow(self.window, "Title contains", 8)
        self.title_not_contains_entry, self.title_not_option = RuleRadioInputRow(self.window, "Title not contains", 10)

        self.body_selector_entry = EntryRow(self.window, 'Body selector', 12, pady=(20, 5))
        self.body_contains_entry, self.body_option = RuleRadioInputRow(self.window, "Body contains", 13)
        self.body_not_contains_entry, self.body_not_option = RuleRadioInputRow(self.window, "Body not contains", 15)

        # Start/Stop scraping
        button_frame = tk.Frame(self.window)
        button_frame.grid(column=1, row=100, sticky="nw", pady=(10, 5))

        self.start_button = tk.Button(button_frame, text="Start Web Scraping", command=self.handle_start_scraping)
        self.start_button.pack(side='left')

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.handle_stop_scraping)
        self.stop_button['state'] = 'disabled'
        self.stop_button.pack(side='left')

        # Load/Save setting
        self.load_setting_button = tk.Button(button_frame, text="Load Setting", command=self.handle_load_setting)
        self.load_setting_button.pack(side='left', padx=(20, 0))

        self.save_setting_button = tk.Button(button_frame, text="Save", command=self.handle_save_setting)
        self.save_setting_button.pack(side='left')

        tk.Label(self.window, text="Output").grid(column=0, row=101, sticky="wn", pady=(0, 5))

        # Textbox for output
        self.output_textbox = Textbox(self.window, height=8, font=('DejaVu Sans Mono', 9, 'normal'), bg='black', fg='white')
        self.output_textbox.grid(column=0, row=102, columnspan=2, sticky="news")

    def handle_close(self):
        self.parent.add_dataset_button['state'] = 'normal'
        self.start_button['state'] = 'normal'
        self.window.destroy()

    def handle_start_scraping(self):
        # create dataset
        self.start_button['state'] = 'disabled'
        dataset_name = self.dataset_name_entry.get()

        payload = {'name': dataset_name}
        response = self.parent.api.post('/api/datasets/', data=payload)
        dataset = json.loads(response.text)

        self.output_textbox.insert_end('Sending request...\nPOST:/api/datasets/\nData: {}\n'.format(payload))

        if response.status_code not in (200, 201):
            self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
            self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
            self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
            self.handle_stop_scraping()
            return

        self.output_textbox.insert_end('Dataset created\n')
        self.url_queue.append(self.start_url_entry.get())

        create_dir()

        url_rule = self.url_contains_entry.get()
        url_opt = self.url_option.get()
        url_not_rule = self.url_not_contains_entry.get()
        url_not_opt = self.url_not_option.get()

        title_rule = self.title_contains_entry.get()
        title_opt = self.title_option.get()
        title_not_rule = self.title_not_contains_entry.get()
        title_not_opt = self.title_not_option.get()

        body_selector = self.body_selector_entry.get()
        body_rule = self.body_contains_entry.get()
        body_opt = self.body_option.get()
        body_not_rule = self.body_not_contains_entry.get()
        body_not_opt = self.body_not_option.get()

        def save_function(document_url, title, title_clean, raw_content):
            resp = self.parent.api.post('/api/documents/', data={'url': document_url, 'title': title, 'title_clean': title_clean, 'raw_content': raw_content, 'content': raw_content, 'dataset': dataset['id']})

            self.output_textbox.insert_end(f'Sending request...\nPOST:/api/documents/\n')
            if resp.status_code not in (200, 201):
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(resp.text), indent=2)))
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                self.handle_stop_scraping()
                return

            self.output_textbox.insert_end('Document created\n')

        def scrape_webpage(thread_id):
            max_document_count = self.max_document_count_entry.get()

            while len(self.url_queue):
                print("----------------------------------")
                url = None
                with self.scraping_lock:
                    if len(self.url_queue) > 0:
                        url = self.url_queue.pop()

                if not url:
                    sleep(2.0)
                else:
                    try:
                        html = get_cached_or_download(url)
                        if not html:
                            continue
                    except Exception:
                        continue

                    with self.scraping_lock:
                        print(url)
                        self.url_downloaded.append(url)
                        soup = BeautifulSoup(html, 'html.parser')

                        title = soup.find('title')
                        print(f'{thread_id} -- {title.text}')

                        links = soup.find_all('a')
                        new_urls = [link.get('href') for link in links]

                        # ------------------------------------------
                        # Add url to crawl
                        #
                        # -- Will ignore title and body rules since
                        #    this codes run first
                        # ------------------------------------------
                        for new_url in new_urls:
                            if not is_absolute(new_url):
                                new_url = urljoin(url, new_url)
                                new_url = urldefrag(new_url)[0]

                            # skip downloaded url
                            if new_url in self.url_downloaded:
                                print(f'{thread_id} -- skip {new_url}. already downloaded')
                                continue

                            # skip already in queue
                            if new_url in self.url_queue:
                                print(f'{thread_id} -- skip {new_url}. already in download queue')
                                continue

                            # skip match not url rule
                            if url_not_rule and test_text(new_url, url_not_rule, url_not_opt):
                                print(f'{thread_id} -- skip {new_url}. matched url_not_rule')
                                continue

                            # download match url rule
                            if test_text(new_url, url_rule, url_opt):
                                print(f'{thread_id} -- Added new url to queue. {new_url}')
                                self.url_queue.append(new_url)

                        # ------------------------------------------
                        # Save document to database
                        # ------------------------------------------
                        if body_selector:
                            body = soup.select(body_selector)
                        else:
                            body = soup.select('body')

                        # skip if match not title rule
                        if title and title_not_rule and test_text(title.text, title_not_rule, title_not_opt):
                            print(f'{thread_id} -- skipped matched not title rule {title_not_rule}')
                            continue

                        # skip if match not body rule
                        if len(body) and body_not_rule:
                            match = False
                            for el in body:
                                if test_text(el.text, body_not_rule, body_not_opt):
                                    match = True

                            if match:
                                print(f'{thread_id} -- skipped matched not body rule {body_not_rule}')
                                continue

                        # store document if match all title and body rules
                        if title and test_text(title.text, title_rule, title_opt):
                            match = False
                            for el in body:
                                if test_text(el.text, body_rule, body_opt):
                                    match = True

                            if match:
                                url_sha1 = hashlib.sha1(url.encode())
                                filename = 'downloads/{}.html'.format(url_sha1.hexdigest())
                                self.matched_document.append(
                                    {'filename': filename, 'body_selector': body_selector, 'title': title.text,
                                     'url': url})
                                print('< '*30)
                                print(f'{thread_id} -- KEEP matched title and body rule')
                                print('< '*30)

                                content = '\n'.join([el.text for el in body])
                                save_function(url, title, title, content)
                                self.document_count += 1

                                if max_document_count and max_document_count.isnumeric():
                                    if self.document_count > int(max_document_count):
                                        break

        t1 = threading.Thread(target=scrape_webpage, args=('thread-1',), daemon=True)
        t1.start()

        t2 = threading.Thread(target=scrape_webpage, args=('thread-2',), daemon=True)
        t2.start()

        t3 = threading.Thread(target=scrape_webpage, args=('thread-3',), daemon=True)
        t3.start()

        t4 = threading.Thread(target=scrape_webpage, args=('thread-4',), daemon=True)
        t4.start()

        self.handle_stop_scraping()

    def handle_stop_scraping(self):
        pass

    def handle_load_setting(self):
        filename = filedialog.askopenfilename(initialdir="presets")

        if not filename:
            return

        settings = load_cfg(filename)

        def set_text(widget, text):
            widget.delete(0, 'end')
            if text:
                widget.insert(0, text)

        def set_option(variable, value):
            if value:
                variable.set(value)
            else:
                variable.set('split')

        set_text(self.start_url_entry, settings['start_url'])
        set_text(self.max_document_count_entry, settings['max_document_count'])

        set_text(self.url_contains_entry, settings['url_rule'])
        set_option(self.url_option, settings['url_option'])
        set_text(self.url_not_contains_entry, settings['url_not_rule'])
        set_option(self.url_not_option, settings['url_not_option'])

        set_text(self.title_contains_entry, settings['title_rule'])
        set_option(self.title_option, settings['title_option'])
        set_text(self.title_not_contains_entry, settings['title_not_rule'])
        set_option(self.title_not_option, settings['title_not_option'])

        set_text(self.body_selector_entry, settings['body_selector'])
        set_text(self.body_contains_entry, settings['body_rule'])
        set_option(self.body_option, settings['body_option'])
        set_text(self.body_not_contains_entry, settings['body_not_rule'])
        set_option(self.body_not_option, settings['body_not_option'])

        self.output_textbox.insert_end("Preset loaded from {}\n".format(filename))

    def handle_save_setting(self):
        f = filedialog.asksaveasfile(defaultextension="cfg", initialdir="presets")

        def write_text(var_name, widget):
            f.write("{}={}\n".format(var_name, widget.get()))

        write_text("start_url", self.start_url_entry)
        write_text("max_document_count", self.max_document_count_entry)

        write_text("url_rule", self.url_contains_entry)
        write_text("url_option", self.url_option)
        write_text("url_not_rule", self.url_not_contains_entry)
        write_text("url_not_option", self.url_not_option)

        write_text("title_rule", self.title_contains_entry)
        write_text("title_option", self.title_option)
        write_text("title_not_rule", self.title_not_contains_entry)
        write_text("title_not_option", self.title_not_option)

        write_text("body_selector", self.body_selector_entry)
        write_text("body_rule", self.body_contains_entry)
        write_text("body_option", self.body_option)
        write_text("body_not_rule", self.body_not_contains_entry)
        write_text("body_not_option", self.body_not_option)

        f.close()

        self.output_textbox.insert_end("Preset saved to {}\n".format(f.name))


class App(WindowSizeMixin):
    def __init__(self):
        super().__init__()
        self.api = None
        self.settings = load_cfg('settings.cfg')

        self.title("NusantaraFood - Web Scraper")
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
        self.dataset_list_frame = tk.Frame(self, padx=5, pady=5, bg="#bbbbbb", width=220)
        self.dataset_list_frame.pack(side="left", fill="y")
        self.dataset_list_frame.pack_propagate(False)
        

        self.dataset_label = tk.Label(self.dataset_list_frame, text="Dataset List", anchor="nw", bg="#bbbbbb")
        self.dataset_label.pack(fill="x", pady=5)

        self.dataset_list_variable = tk.Variable(value=[])
        self.dataset_listbox = DbListbox(self.dataset_list_frame, self.dataset_list_variable, handle_select=self.handle_dataset_selected)

        self.add_dataset_button = tk.Button(self.dataset_list_frame, text="Add Dataset", command=self.handle_show_add_dataset_window)
        self.add_dataset_button['state'] = 'disabled'
        self.add_dataset_button.pack(side="left", anchor="nw", pady=5)

        self.delete_dataset_button = tk.Button(self.dataset_list_frame, text="Delete", command=self.handle_delete_dataset)
        self.delete_dataset_button['state'] = 'disabled'
        self.delete_dataset_button.pack(side="left", anchor="nw", pady=5)

        # ------------------------------------------
        # 2nd Column (Dataset details)
        # ------------------------------------------
        self.dataset_detail_frame = tk.Frame(self, width=220, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        _, self.dataset_id_label = StackedLabels(self.dataset_detail_frame, "Dataset ID:", "-", bg="#cccccc", width=30)
        _, self.dataset_name_label = StackedLabels(self.dataset_detail_frame, "Dataset Name:", "-", bg="#cccccc", width=30)
        _, self.dataset_source_label = StackedLabels(self.dataset_detail_frame, "Source:", "-", bg="#cccccc", width=30)
        _, self.dataset_document_count_label = StackedLabels(self.dataset_detail_frame, "Document Count:", "-", bg="#cccccc", width=30)

        self.clean_dataset_button = tk.Button(self.dataset_detail_frame, text="Clean Dataset", command=self.handle_clean_dataset)
        self.clean_dataset_button.pack(side="left", anchor="nw", pady=5)

        # ------------------------------------------
        # 3rd Column (Document list)
        # ------------------------------------------
        self.document_list_frame = tk.Frame(self, width=220, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")
        self.document_list_frame.pack_propagate(False)

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = DbListbox(self.document_list_frame, self.document_list_variable, width=25, handle_select=self.handle_document_selected)

        self.delete_document_button = tk.Button(self.document_list_frame, text="Delete Document", command=self.handle_delete_document)
        self.delete_document_button.pack(anchor="nw", pady=5)

        # ------------------------------------------
        # 4th Column (Document details)
        # ------------------------------------------
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both", expand=True)

        _, self.document_title_label = StackedLabels(self.document_detail_frame, "Document Title:", "-", bg="#eeeeee", width=35)
        _, self.document_title_cleaned_label = StackedLabels(self.document_detail_frame, "Document Title (Cleaned):", "-", bg="#eeeeee", width=35)

        tk.Label(self.document_detail_frame, text="Raw Content", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.document_raw_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_raw_content_textbox.pack(pady=(0, 5), fill="x")

        tk.Label(self.document_detail_frame, text="Content", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.document_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_content_textbox.pack(pady=(0, 5), fill="x")

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

        # Allow add dataset because connect to host successful
        self.add_dataset_button['state'] = 'normal'
        self.delete_dataset_button['state'] = 'normal'

        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return

        self.dataset_listbox.delete(0, 'end')
        for item in data:
            text = '#{} - {}'.format(item['id'], item['name'])
            self.dataset_listbox.insert('end', text)

    def handle_dataset_selected(self, event):
        dataset_id, dataset_name = self.dataset_listbox.get_selection()
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
        self.document_content_textbox.set_text(data['content'])

        if 'raw_content' in data:
            self.document_raw_content_textbox.set_text(data['raw_content'])

    def handle_delete_dataset(self):
        dataset_id, dataset_name = self.dataset_listbox.get_selection()

        # Do nothing when dataset selection empty
        if not dataset_id:
            return

        # Delete dataset
        url = '/api/datasets/{}'.format(dataset_id)
        response = self.api.delete(url)
        if response.status_code not in (200, 204,):
            if response.text:
                data = json.loads(response.text)
                messagebox.showerror('error', data['detail'])
            return

        # Update dataset list
        index = self.dataset_listbox.curselection()
        self.dataset_listbox.delete(index)

    def handle_delete_document(self):
        document_id, document_name = self.document_listbox.get_selection()

        # Do nothing when document selection empty
        if not document_id:
            return

        # Delete document
        url = '/api/documents/{}'.format(document_id)
        response = self.api.delete(url)
        if response.status_code not in (200, 204, ):
            if response.text:
                data = json.loads(response.text)
                messagebox.showerror('error', data['detail'])
            return

        # Update document list
        index = self.document_listbox.curselection()
        self.document_listbox.delete(index)

    def handle_clean_dataset(self):
        self.clean_dataset_window = CleanDatasetWindow(self)

    # Sub window
    def handle_show_add_dataset_window(self):
        self.add_dataset_window = AddDatasetWindow(self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
