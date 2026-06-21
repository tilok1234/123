import customtkinter as ctk

class TooltipPreview(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#1e1e24", corner_radius=8, border_width=2, border_color="#555566", **kwargs)

        self.pack_propagate(False)
        self.configure(width=280, height=400)

        # Name
        self.name_lbl = ctk.CTkLabel(self, text="Item Name", font=("Arial", 18, "bold"), text_color="#ffd700", anchor="w")
        self.name_lbl.pack(fill="x", padx=10, pady=(10, 2))

        # Type Line (Category / Subcategory)
        self.type_lbl = ctk.CTkLabel(self, text="Item Type", font=("Arial", 12, "italic"), text_color="#aaaaaa", anchor="w")
        self.type_lbl.pack(fill="x", padx=10, pady=(0, 10))

        # Separator
        sep1 = ctk.CTkFrame(self, height=2, fg_color="#555566")
        sep1.pack(fill="x", padx=5, pady=5)

        # Stats Frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=10, pady=5)
        self.stat_labels = []

        # Details/Notes Frame
        self.details_lbl = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="#cccccc", anchor="nw", justify="left", wraplength=250)
        self.details_lbl.pack(fill="both", expand=True, padx=10, pady=5)

    def update_preview(self, data):
        # Name
        name = data.get("display_name") or data.get("name") or "Unnamed Item"
        self.name_lbl.configure(text=name)

        # Type
        tax = data.get("taxonomy", {})
        cat = tax.get("category", "").capitalize()
        subcat = tax.get("subcategory", "").capitalize()
        type_str = f"{cat} - {subcat}" if subcat else cat
        self.type_lbl.configure(text=type_str)

        # Clear old stats
        for lbl in self.stat_labels:
            lbl.destroy()
        self.stat_labels.clear()

        # Add new stats
        row = 0

        # Handle equipment stats
        if "stats" in data:
            stats = data["stats"]
            for stat in ["dmg", "cooldown", "range", "str", "hp", "dex", "atk", "vit", "spd"]:
                val = stats.get(stat)
                if val and float(val) > 0:
                    lbl = ctk.CTkLabel(self.stats_frame, text=f"+{val} {stat.upper()}", font=("Arial", 12, "bold"), text_color="#88ff88", anchor="w")
                    lbl.grid(row=row, column=0, sticky="w", pady=1)
                    self.stat_labels.append(lbl)
                    row += 1

            pattern = stats.get("projectile_pattern")
            if pattern:
                lbl = ctk.CTkLabel(self.stats_frame, text=f"Pattern: {pattern}", font=("Arial", 12), text_color="#aaaaff", anchor="w")
                lbl.grid(row=row, column=0, sticky="w", pady=1)
                self.stat_labels.append(lbl)
                row += 1

        # Handle ingredient/recipe specific props
        if "base_value" in data:
            lbl = ctk.CTkLabel(self.stats_frame, text=f"Value: {data.get('base_value', 0)}g", font=("Arial", 12), text_color="#ffffaa", anchor="w")
            lbl.grid(row=row, column=0, sticky="w", pady=1)
            self.stat_labels.append(lbl)
            row += 1

        # Details / Notes
        notes = data.get("notes", "")
        self.details_lbl.configure(text=notes)
