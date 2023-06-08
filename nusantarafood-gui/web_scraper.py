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

        self.dataset_list_variable = tk.Variable(value=['item {}'.format(x) for x in range(100)])

        self.dataset_listbox_frame = tk.Frame(self.dataset_list_frame, bg="#bbbbbb")
        self.dataset_listbox_frame.pack()
        self.dataset_listbox = tk.Listbox(self.dataset_listbox_frame, width=30, height=25, listvariable=self.dataset_list_variable)
        self.dataset_listbox.pack(side="left")
        self.dataset_listbox_scroll = tk.Scrollbar(self.dataset_listbox_frame)
        self.dataset_listbox_scroll.pack(side="right", fill="y")

        self.dataset_listbox.config(yscrollcommand=self.dataset_listbox_scroll.set)
        self.dataset_listbox_scroll.config(command=self.dataset_listbox.yview)

        self.add_dataset_button = tk.Button(self.dataset_list_frame, text="Add Dataset")
        self.add_dataset_button.pack(anchor="nw", pady=5)

        # Dataset Detail Column
        self.dataset_detail_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#cccccc")
        self.dataset_detail_frame.pack(side="left", fill="y")
        self.dataset_detail_frame.pack_propagate(0)

        self.add_dataset_detail_label("Dataset Name")
        self.add_dataset_detail_value("Azie_udang")
        self.add_dataset_detail_label("Source")
        self.add_dataset_detail_value("azieudang.jl")
        self.add_dataset_detail_label("Stopwords Count")
        self.add_dataset_detail_value("65411")
        self.add_dataset_detail_label("Document Count")
        self.add_dataset_detail_value("500")

        # Document List Column
        self.document_list_frame = tk.Frame(self, width=250, padx=5, pady=5, bg="#dddddd")
        self.document_list_frame.pack(side="left", fill="y")

        tk.Label(self.document_list_frame, text="Document List", anchor="nw", bg="#dddddd", fg="#666666", width=30).pack(pady=5, fill="x")

        self.document_list_variable = tk.Variable(value=['document {}'.format(x) for x in range(100)])
        self.document_listbox = self.add_listbox(self.document_list_frame, self.document_list_variable)

    def add_dataset_detail_label(self, text, fg="#666666", pady=(5, 0)):
        widget = tk.Label(self.dataset_detail_frame, text=text, anchor="nw", bg="#cccccc", width=30, fg=fg)
        widget.pack(pady=pady, fill="x")
        return widget

    def add_dataset_detail_value(self, text):
        return self.add_dataset_detail_label(text, fg="#000000", pady=(0, 5))

    @staticmethod
    def add_listbox(parent, variable):
        listbox_frame = tk.Frame(parent, bg="#bbbbbb")
        listbox_frame.pack()

        listbox = tk.Listbox(listbox_frame, width=30, height=25, listvariable=variable)
        listbox.pack(side="left")

        listbox_scroll = tk.Scrollbar(listbox_frame)
        listbox_scroll.pack(side="right", fill="y")

        listbox.config(yscrollcommand=listbox_scroll.set)
        listbox_scroll.config(command=listbox.yview)

        return listbox


if __name__ == "__main__":
    app = App()
    app.mainloop()
