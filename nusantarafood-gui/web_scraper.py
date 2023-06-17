import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox
import requests
from urllib.parse import urljoin, urlparse, urldefrag
import json
import re
import hashlib
import os
from bs4 import BeautifulSoup


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
        self.add_dataset_button['state'] = 'disabled'
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

        self.start_button = None
        self.stop_button = None
        self.output_textbox = None
        self.url_downloaded = []
        self.url_queue = []
        self.url_queue_lock = threading.Lock()
        self.scraping_lock = threading.Lock()
        self.matched_document = []

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
        def add_entry(label, row, pady=(0, 5)):
            tk.Label(add_dataset_window, text=label).grid(column=0, row=row, sticky="w", pady=pady, padx=(0, 10))
            widget = tk.Entry(add_dataset_window, width=50)
            widget.grid(column=1, row=row, sticky="new", pady=pady)
            return widget

        dataset_name_entry = add_entry("Dataset Name", 0)
        max_document_count_entry = add_entry("Max Num. of Document", 1)
        start_url_entry = add_entry("Starting Url", 2)

        tk.Label(add_dataset_window, text="Rules").grid(column=0, row=3, sticky="nw", pady=(20, 5))

        def print_options():
            print(url_var.get())
            print(url_not_var.get())
            print(title_var.get())
            print(title_not_var.get())
            print(body_var.get())
            print(body_not_var.get())

        def add_rule_entry(label, row):
            widget = add_entry(label, row)
            frame = tk.Frame(add_dataset_window)
            frame.grid(column=1, row=row+1, sticky="new", pady=(0, 5))
            var = tk.StringVar(value="split")
            split_comma_option = tk.Radiobutton(frame, variable=var, value="split", text="split comma", command=print_options)
            split_comma_option.pack(side="left")
            re_match_option = tk.Radiobutton(frame, variable=var, value="re.match", text="re.match", command=print_options)
            re_match_option.pack(side="left")
            re_search_option = tk.Radiobutton(frame, variable=var, value="re.search", text="re.search", command=print_options)
            re_search_option.pack(side="left")

            return widget, var

        url_contains_entry, url_var = add_rule_entry("Url contains", 4)
        url_not_contains_entry, url_not_var = add_rule_entry("Url not contains", 6)
        title_contains_entry, title_var = add_rule_entry("Title contains", 8)
        title_not_contains_entry, title_not_var = add_rule_entry("Title not contains", 10)
        body_selector_entry = add_entry('Body selector', 12, pady=(20,5))
        body_contains_entry, body_var = add_rule_entry("Body contains", 13)
        body_not_contains_entry, body_not_var = add_rule_entry("Body not contains", 15)

        def is_absolute(url):
            return bool(urlparse(url).netloc)

        def get_cached_or_download(url):
            url_sha1 = hashlib.sha1(url.encode())
            filename = 'downloads/{}.html'.format(url_sha1.hexdigest())
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    print('Loaded from file {}'.format(filename))
                    return f.read()
            else:
                response = requests.get(url)
                if response.status_code == 200:
                    print('Downloaded {} from url {}'.format(filename, url))
                    with open(filename, 'w') as f:
                        f.write(response.text)

                    return response.text

            print('Failed to get {}'.format(url))
            return None

        def test_rule(text, rule, option):
            result = False
            if not rule:
                return True

            if option == 'split':
                match = False
                for kw in rule.split(','):
                    if kw in text:
                        match = True
                        continue
                if match:
                    result = True
            elif option == 're.match':
                if re.match(rule, text):
                    result = True
            elif option == 're.search':
                if re.search(rule, text):
                    result = True

            return result

        def scrape_webpage(thread_id, save_function, url_rule, url_opt, url_not_rule, url_not_opt, title_rule, title_opt, title_not_rule, title_not_opt, body_selector, body_rule, body_opt, body_not_rule, body_not_opt):
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

                        if body_selector:
                            body = soup.select(body_selector)
                        else:
                            body = soup.select('body')

                        # skip if match not title rule
                        if title and title_not_rule and test_rule(title.text, title_not_rule, title_not_opt):
                            print(f'{thread_id} -- skipped matched not title rule {title_not_rule}')
                            continue

                        # skip if match not body rule
                        if len(body) and body_not_rule:
                            match = False
                            for el in body:
                                if test_rule(el, body_not_rule, body_not_opt):
                                    match = True

                            if match:
                                print(f'{thread_id} -- skipped matched not body rule {body_not_rule}')
                                continue

                        # store document if match title and body rules
                        if title and test_rule(title.text, title_rule, title_opt):
                            match = False
                            for el in body:
                                if test_rule(el, body_rule, body_opt):
                                    match = True

                            if match:
                                url_sha1 = hashlib.sha1(url.encode())
                                filename = 'downloads/{}.html'.format(url_sha1.hexdigest())
                                self.matched_document.append({'filename': filename, 'body_selector': body_selector, 'title': title.text, 'url': url})
                                print(f'{thread_id} -- KEEP matched title and body rule')

                                content = '\n'.join([el.text for el in body])
                                save_function(url, title, title, content)

                        links = soup.find_all('a')
                        new_urls = [link.get('href') for link in links]

                        for new_url in new_urls:
                            if not is_absolute(new_url):
                                new_url = urljoin(url, new_url)
                                new_url = urldefrag(new_url)[0]

                            # skip downloaded url
                            if new_url in self.url_downloaded:
                                print(f'{thread_id} -- skip {new_url}. already downloaded')
                                continue

                            if new_url in self.url_queue:
                                print(f'{thread_id} -- skip {new_url}. already in download queue')
                                continue

                            # skip match not url rule
                            if url_not_rule and test_rule(new_url, url_not_rule, url_not_opt):
                                print(f'{thread_id} -- skip {new_url}. matched url_not_rule')
                                continue

                            # download match url rule
                            if test_rule(new_url, url_rule, url_opt):
                                print(f'{thread_id} -- Added new url to queue. {new_url}')
                                self.url_queue.append(new_url)


        def handle_start_scraping():
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'

            # create dataset
            dataset_name = dataset_name_entry.get()

            payload = {'name': dataset_name}
            response = self.api.post('/api/datasets/', data=payload)
            dataset = json.loads(response.text)

            self.output_textbox.insert_end('Sending request...\nPOST:/api/datasets/\nData: {}\n'.format(payload))
            if response.status_code not in (200, 201):
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                handle_stop_scraping()
                return

            self.output_textbox.insert_end('Dataset created\n')
            self.url_queue.append(start_url_entry.get())

            url_contains = url_contains_entry.get()
            url_contains_opt = url_var.get()
            url_not_contains = url_not_contains_entry.get()
            url_not_contains_opt = url_not_var.get()

            title_contains = title_contains_entry.get()
            title_contains_opt = title_var.get()
            title_not_contains = title_not_contains_entry.get()
            title_not_contains_opt = title_not_var.get()

            body_selector = body_selector_entry.get()
            body_contains = body_contains_entry.get()
            body_contains_opt = body_var.get()
            body_not_contains = body_not_contains_entry.get()
            body_not_contains_opt = body_not_var.get()

            def save_function(document_url, title, title_clean, raw_content):
                resp = self.api.post('/api/documents/', data={'url': document_url, 'title': title, 'title_clean': title_clean, 'raw_content': raw_content, 'content': raw_content, 'dataset': dataset['id']})

                self.output_textbox.insert_end(f'Sending request...\nPOST:/api/documents/\n')
                if resp.status_code not in (200, 201):
                    self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(resp.text), indent=2)))
                    self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    handle_stop_scraping()
                    return

                self.output_textbox.insert_end('Document created\n')

            thread_args = (save_function,
                           url_contains, url_contains_opt, url_not_contains, url_not_contains_opt,
                           title_contains, title_contains_opt, title_not_contains, title_not_contains_opt,
                           body_selector, body_contains, body_contains_opt, body_not_contains, body_not_contains_opt)

            t1 = threading.Thread(target=scrape_webpage, args=('thread-1', *thread_args), daemon=True)
            t1.start()

            t2 = threading.Thread(target=scrape_webpage, args=('thread-2', *thread_args), daemon=True)
            t2.start()

            t3 = threading.Thread(target=scrape_webpage, args=('thread-3', *thread_args), daemon=True)
            t3.start()

            t4 = threading.Thread(target=scrape_webpage, args=('thread-4', *thread_args), daemon=True)
            t4.start()

            handle_stop_scraping()

        def handle_stop_scraping():
            self.start_button['state'] = 'normal'
            self.stop_button['state'] = 'disabled'
            print("stop scraping")

        button_frame = tk.Frame(add_dataset_window)
        button_frame.grid(column=1, row=100, sticky="nw", pady=(10, 5))

        self.start_button = tk.Button(button_frame, text="Start Web Scraping", command=handle_start_scraping)
        self.start_button.pack(side='left', padx=(0, 5))

        self.stop_button = tk.Button(button_frame, text="Stop", command=handle_stop_scraping)
        self.stop_button['state'] = 'disabled'
        self.stop_button.pack(side='left')

        tk.Label(add_dataset_window, text="Output").grid(column=0, row=101, sticky="wn", pady=(0, 5))

        # Textbox for output
        self.output_textbox = Textbox(add_dataset_window, height=8, font=('DejaVu Sans Mono', 9, 'normal'), bg='black', fg='white')
        self.output_textbox.grid(column=0, row=102, columnspan=2, sticky="news")


if __name__ == "__main__":
    app = App()
    app.mainloop()
