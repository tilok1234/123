import customtkinter as ctk

class DynamicRowContainer(ctk.CTkScrollableFrame):
    def __init__(self, master, state, title, tracking_list_name, get_options_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state
        self.title = title
        self.tracking_list_name = tracking_list_name
        self.get_options_callback = get_options_callback

        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", pady=2)

        ctk.CTkLabel(self.header, text=title, font=("Arial", 14, "bold")).pack(side="left", padx=5)
        ctk.CTkButton(self.header, text="+ Add", width=50, command=self.add_row).pack(side="right", padx=5)

        self.rows_frame = ctk.CTkFrame(self)
        self.rows_frame.pack(fill="both", expand=True)

    def get_tracking_list(self):
        return getattr(self.state, self.tracking_list_name)

    def add_row(self, key_val="", qty_val="1"):
        row_frame = ctk.CTkFrame(self.rows_frame)
        row_frame.pack(fill="x", pady=2, padx=5)

        options = self.get_options_callback()
        if not options:
            options = ["-- No Options --"]

        key_combo = ctk.CTkComboBox(row_frame, values=options, width=150)
        key_combo.pack(side="left", padx=5)
        if key_val and key_val in options:
            key_combo.set(key_val)
        elif options and options[0] != "-- No Options --":
            key_combo.set(options[0])

        qty_entry = ctk.CTkEntry(row_frame, width=50)
        qty_entry.pack(side="left", padx=5)
        qty_entry.insert(0, str(qty_val))

        remove_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", hover_color="darkred",
                                   command=lambda f=row_frame: self.remove_row(f))
        remove_btn.pack(side="right", padx=5)

        record = {
            "frame": row_frame,
            "combo": key_combo,
            "qty": qty_entry
        }
        self.get_tracking_list().append(record)

    def remove_row(self, row_frame):
        row_frame.destroy()
        tracking_list = self.get_tracking_list()
        # Remove from tracking list
        new_list = [r for r in tracking_list if r["frame"] != row_frame]
        setattr(self.state, self.tracking_list_name, new_list)

    def clear_rows(self):
        for record in self.get_tracking_list():
            record["frame"].destroy()
        setattr(self.state, self.tracking_list_name, [])

    def refresh_options(self):
        options = self.get_options_callback()
        if not options:
            options = ["-- No Options --"]

        for record in self.get_tracking_list():
            current_val = record["combo"].get()
            record["combo"].configure(values=options)
            if current_val in options:
                record["combo"].set(current_val)
            elif options:
                record["combo"].set(options[0])

    def get_data(self):
        data = {}
        for record in self.get_tracking_list():
            key = record["combo"].get()
            qty = record["qty"].get()
            if key != "-- No Options --":
                data[key] = qty
        return data
