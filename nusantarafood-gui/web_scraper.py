import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("NusantaraFood - Web Scraper")
        self.geometry("1000x600")

        # Dataset List Column
        self.dataset_list_frame = tk.Frame(self, padx=5, pady=5, bg="#bbbbbb")
        self.dataset_list_frame.pack(side="left", fill="y")

        self.dataset_label = tk.Label(self.dataset_list_frame, text="Dataset List", anchor="nw", bg="#bbbbbb")
        self.dataset_label.pack(fill="x", pady=5)

        self.dataset_list_variable = tk.Variable(value=[])
        self.dataset_listbox = self.add_listbox(self.dataset_list_frame, self.dataset_list_variable)

        self.add_dataset_button = tk.Button(self.dataset_list_frame, text="Add Dataset", command=self.show_add_dataset_window)
        self.add_dataset_button.pack(anchor="nw", pady=5)

        # Dataset Detail Column
        self.dataset_detail_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        self.add_dataset_detail_label("Dataset Name")
        self.add_dataset_detail_value("-")
        self.add_dataset_detail_label("Source")
        self.add_dataset_detail_value("-")
        self.add_dataset_detail_label("Stopwords Count")
        self.add_dataset_detail_value("-")
        self.add_dataset_detail_label("Document Count")
        self.add_dataset_detail_value("-")

        # Document List Column
        self.document_list_frame = tk.Frame(self, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd").pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=[])
        self.document_listbox = self.add_listbox(self.document_list_frame, self.document_list_variable, width=25)

        self.delete_document_button = tk.Button(self.document_list_frame, text="Delete Document", state="disabled")
        self.delete_document_button.pack(anchor="nw", pady=5)

        # Document Detail Column
        self.document_detail_frame = tk.Frame(self, padx=5, pady=5, bg="#eeeeee")
        self.document_detail_frame.pack(side="left", fill="both")

        self.add_document_detail_label("Document Title")
        self.add_document_detail_value("-")
        self.add_document_detail_label("Document Title (Cleaned)")
        self.add_document_detail_value("-")
        self.add_document_detail_label("Raw Content")
        self.add_textbox(self.document_detail_frame)

        self.add_document_detail_label("Selected Content")
        self.add_textbox(self.document_detail_frame)

        self.add_document_detail_label("Content Selector")
        self.add_textbox(self.document_detail_frame, height=1, pady=0)

        self.apply_selector_button = tk.Button(self.document_detail_frame, text="Apply", state='disabled')
        self.apply_selector_button.pack(anchor="nw", pady=5)

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
            widget.grid(column=1, row=row, sticky="ne", pady=(0, 5))
            return widget

        add_textbox("Dataset Name", 0)
        add_textbox("Max Num. of Document", 1)
        add_textbox("Starting Url", 2)

        tk.Label(add_dataset_window, text="Regex Rule").grid(column=0, row=3, sticky="nw", pady=(20, 5))
        add_textbox("Url", 4)
        add_textbox("Title", 5)
        add_textbox("Content", 6)

        start_button = tk.Button(add_dataset_window, text="Start Web Scraping")
        start_button.grid(column=1, row=7, sticky="nw", pady=(10, 5))

        table_frame = tk.Frame(add_dataset_window, borderwidth=1, relief='solid')
        table_frame.grid(column=0, row=8, columnspan=2, sticky="news")

        def add_row(row, num, page_title, content_length):
            tk.Label(table_frame, borderwidth=1, relief='solid', anchor="nw", width=5, text=num).grid(column=0, row=row, sticky="nw")
            tk.Label(table_frame, borderwidth=1, relief='solid', anchor="nw", width=50, text=page_title).grid(column=1, row=row, sticky="nw")
            tk.Label(table_frame, borderwidth=1, relief='solid', anchor="nw", width=17, text=content_length).grid(column=2, row=row, sticky="nw")

        def add_row2(num, page_title, content_length):
            row_frame = tk.Frame(table_frame)
            row_frame.pack(expand=True, fill="both")
            tk.Label(row_frame, borderwidth=1, relief='solid', anchor="nw", padx=5, pady=3, width=5, text=num).pack(side="left")
            tk.Label(row_frame, borderwidth=1, relief='solid', anchor="nw", padx=5, pady=3, text=page_title).pack(side="left", fill="x", expand=True)
            tk.Label(row_frame, borderwidth=1, relief='solid', anchor="nw", padx=5, pady=3, width=17, text=content_length).pack(side="left")

        add_row2("#", "Page Title", "Content Length")
        add_row2("#", "Page Title", "Content Length")


if __name__ == "__main__":
    app = App()
    app.mainloop()
