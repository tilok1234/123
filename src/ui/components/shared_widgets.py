import customtkinter as ctk

def create_labeled_entry(parent, label_text, row, col, default_val="", width=200):
    ctk.CTkLabel(parent, text=label_text).grid(row=row, column=col, sticky="w", padx=5, pady=2)
    entry = ctk.CTkEntry(parent, width=width)
    entry.grid(row=row, column=col+1, sticky="w", padx=5, pady=2)
    entry.insert(0, str(default_val))
    return entry

def create_labeled_textbox(parent, label_text, row, col, default_val="", width=200, height=100):
    ctk.CTkLabel(parent, text=label_text).grid(row=row, column=col, sticky="nw", padx=5, pady=2)
    textbox = ctk.CTkTextbox(parent, width=width, height=height)
    textbox.grid(row=row, column=col+1, sticky="w", padx=5, pady=2)
    if default_val:
        textbox.insert("1.0", str(default_val))
    return textbox
