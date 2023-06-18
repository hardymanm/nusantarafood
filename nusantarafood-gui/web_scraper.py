import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox, filedialog
import requests
from urllib.parse import urljoin, urlparse, urldefrag
import json
import re
import hashlib
import os
from bs4 import BeautifulSoup
import types


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


def EntryRow(parent, text="", row=None, pady=(0, 5), **kwargs):
    tk.Label(parent, text=text).grid(column=0, row=row, sticky="w", pady=pady, padx=(0, 10))
    widget = tk.Entry(parent, width=50, **kwargs)
    widget.grid(column=1, row=row, sticky="new", pady=pady)
    return widget


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


def is_absolute(url):
    return bool(urlparse(url).netloc)


def create_download_dir(path="downloads"):
    if not os.path.exists(path):
        os.mkdir(path)


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
        self.window.destroy()

    def handle_start_scraping(self):
        # create dataset
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

        create_download_dir()

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
                url = None
                with self.scraping_lock:
                    if len(self.url_queue) > 0:
                        url = self.url_queue.pop()

                if not url:
                    sleep(2.0)
                else:
                    html = get_cached_or_download(url)
                    if not html:
                        continue

                    with self.scraping_lock:
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
                                print(f'{thread_id} -- KEEP matched title and body rule')

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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.api = None
        self.settings = load_cfg('settings.cfg')

        self.title("NusantaraFood - Web Scraper")
        self.geometry("1000x600")

        # ------------------------------------------
        # Sub-window (Add dataset)
        # ------------------------------------------
        self.add_dataset_window = None

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

        self.add_dataset_button = tk.Button(self.dataset_list_frame, text="Add Dataset", command=self.handle_show_add_dataset_window)
        self.add_dataset_button['state'] = 'disabled'
        self.add_dataset_button.pack(anchor="nw", pady=5)

        # ------------------------------------------
        # 2nd Column (Dataset details)
        # ------------------------------------------
        self.dataset_detail_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        _, self.dataset_name_label = StackedLabels(self.dataset_detail_frame, "Dataset Name:", "-", bg="#cccccc", width=30)
        _, self.dataset_source_label = StackedLabels(self.dataset_detail_frame, "Source:", "-", bg="#cccccc", width=30)
        _, self.dataset_document_count_label = StackedLabels(self.dataset_detail_frame, "Document Count:", "-", bg="#cccccc", width=30)

        # ------------------------------------------
        # 3rd Column (Document list)
        # ------------------------------------------
        self.document_list_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = DbListbox(self.document_list_frame, self.document_list_variable, width=25, handle_select=self.handle_document_selected)

        self.delete_document_button = tk.Button(self.document_list_frame, text="Delete Document", state="disabled")
        self.delete_document_button.pack(anchor="nw", pady=5)

        # ------------------------------------------
        # 4th Column (Document details)
        # ------------------------------------------
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both")

        _, self.document_title_label = StackedLabels(self.document_detail_frame, "Document Title:", "-", bg="#eeeeee", width=35)
        _, self.document_title_cleaned_label = StackedLabels(self.document_detail_frame, "Document Title (Cleaned):", "-", bg="#eeeeee", width=35)

        tk.Label(self.document_detail_frame, text="Raw Content", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.document_raw_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_raw_content_textbox.pack(pady=(0, 5))

        tk.Label(self.document_detail_frame, text="Content", anchor="nw", bg="#eeeeee", width=35).pack(pady=(5, 0), fill="x")
        self.document_content_textbox = Textbox(self.document_detail_frame, height=8)
        self.document_content_textbox.pack(pady=(0, 5))

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

    # Sub window
    def handle_show_add_dataset_window(self):
        self.add_dataset_window = AddDatasetWindow(self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
