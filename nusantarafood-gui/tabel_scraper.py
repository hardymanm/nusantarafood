import json
from imports.utils import *
from imports.ui import *
from imports.client import Api
import threading
import tkinter as tk
from tkinter import messagebox
import requests


class ScrapeTableWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.scrape_tabel_button['state'] = 'disabled'
        
        # ------------------------------------------
        # UI Construct
        # ------------------------------------------
        self.window = tk.Toplevel(parent, padx=5, pady=5)
        self.window.title("Scrape Tabel")
        self.window.protocol("WM_DELETE_WINDOW", self.handle_close)
        self.window.geometry("640x480")
        
        self.scrape_button = tk.Button(self.window, text="Scrape", command=self.handle_scrape)
        self.scrape_button.pack()
        self.output_textbox = Textbox(self.window, height=8, font=('DejaVu Sans Mono', 9, 'normal'), bg='black', fg='white')
        self.output_textbox.pack(fill="both", expand=True)
        
    
    def handle_scrape(self):
        categories = []
        try:
            response = self.parent.api.get(f"/api/food-categories/?fields=id,items")
            
        except Exception:
            messagebox.showerror("Request Failed", f"/api/food-categories/?fields=id,items")
            return

        if response.status_code not in (200, 201):
            self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
            self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
            self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
            return
            
        categories = [(cat['id'], set(re.findall(r'[\w ]+', cat['items'].lower()))) for cat in json.loads(response.text)]
        def get_tabel_categories(title):
            matching_ids = []
            title = re.findall(r'(\w+)', title.lower())
            for id, member_set in categories:
                match = set(title).intersection(member_set)
                if len(match):
                    matching_ids.append(id)

            print(matching_ids)
            return matching_ids
        
        def scrape():
            dataset_id = self.parent.dataset_id_label["text"]

            try:
                response = self.parent.api.get(f"/api/documents/?dataset={dataset_id}&fields=id,title_clean")
            except Exception:
                messagebox.showerror("Request Failed", f"GET request error /api/documents/?dataset={dataset_id}&fields=id,title_clean")
                return

            if response.status_code not in (200, 201):
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                return

            documents = json.loads(response.text)
            for document in documents:
                categories = get_tabel_categories(document['title_clean'])
                
                self.output_textbox.insert_end(f"{document['title_clean']}\n")
                
                payload = {'generated_categories': categories}
                response = self.parent.api.patch(f"/api/documents/{document['id']}/", json=payload)
                if response.status_code not in (200, 201):
                    self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ERROR ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    self.output_textbox.insert_end('{}\n'.format(json.dumps(json.loads(response.text), indent=2)))
                    self.output_textbox.insert_end('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n')
                    return

                self.output_textbox.insert_end(f"PATCH /api/documents/{document['id']}/\n\n")
                print(f"PATCH /api/documents/{document['id']}/")
            
            self.output_textbox.insert_end(f"Done.\n")


        thread = threading.Thread(target=scrape, daemon=True)
        thread.start()
    
    def handle_close(self):
        self.parent.scrape_tabel_button['state'] = 'normal'
        self.window.destroy()


class App(WindowSizeMixin):
    def __init__(self):
        super().__init__()
        self.api = None
        self.settings = load_cfg('settings.cfg')

        self.title("NusantaraFood - Tabel 1981 Scraper")
        
        # ------------------------------------------
        # Food categories labels (id -> names)
        # ------------------------------------------
        self.categories = dict()

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

        _, self.dataset_id_label = StackedLabels(self.dataset_detail_frame, "[Dataset ID]", "-", bg="#cccccc", width=30)
        _, self.dataset_name_label = StackedLabels(self.dataset_detail_frame, "[Dataset Name]", "-", bg="#cccccc", width=30)
        _, self.dataset_source_label = StackedLabels(self.dataset_detail_frame, "[Source]", "-", bg="#cccccc", width=30)

        self.scrape_tabel_button = tk.Button(self.dataset_detail_frame, text="Scrape Tabel 1981", command=self.handle_scrape_tabel)
        self.scrape_tabel_button.pack(anchor="nw")

        # ------------------------------------------
        # 3rd Column (Document list)
        # ------------------------------------------
        self.document_list_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = DbListbox(self.document_list_frame, self.document_list_variable, width=25, handle_select=self.handle_document_selected)

        # ------------------------------------------
        # 4th Column (Document details)
        # ------------------------------------------
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both")
        
        _, self.document_title_label = StackedLabels(self.document_detail_frame, "[Document Title]", "-", bg="#eeeeee", width=35)
        _, self.document_title_cleaned_label = StackedLabels(self.document_detail_frame, "[Document Title (Cleaned)]", "-", bg="#eeeeee", width=35)
        _, self.document_generated_categories_label = StackedLabels(self.document_detail_frame, "[Generated Categories]", "-", bg="#eeeeee", width=35)
        

    def handle_scrape_tabel(self):
        self.scrape_tabel_window = ScrapeTableWindow(self)

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
            
            
        # get food categories
        try:
            response = self.api.get("/api/food-categories/?fields=id,name,name_en")
            
        except Exception as err:
            messagebox.showerror("Request Failed", f"/api/food-categories/?fields=id,name,name_en")
            print(err)
            return

        if response.status_code not in (200, 201):
            # err
            return
        
        for c in json.loads(response.text):
            self.categories[c['id']] = f'{c["name"]} ({c["name_en"]})'

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

    def handle_document_selected(self, event):
        document_id, document_name = self.document_listbox.get_selection()

        # Do nothing when document selection empty
        if not document_id:
            return

        # Update document list
        url = '/api/documents/{}/?fields=title,title_clean,generated_categories'.format(document_id)
        response = self.api.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            messagebox.showerror('error', data['detail'])
            return
        
        self.document_title_label.config(text=data['title'])
        self.document_title_cleaned_label.config(text=data['title_clean'])
        
        tmp = []
        for category in data['generated_categories']:
            tmp.append(self.categories[category])
        
        self.document_generated_categories_label.config(text="\n".join(tmp))
        

if __name__ == "__main__":
    app = App()
    app.mainloop()
