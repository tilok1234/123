import customtkinter as ctk
from src.state.taxonomy import CATEGORIES, ZONES, FACTIONS
from src.services.validation_service import sanitize_id

class TaxonomyGenerator(ctk.CTkFrame):
    def __init__(self, master, force_category=None, allowed_categories=None, on_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.force_category = force_category
        self.allowed_categories = allowed_categories
        self.on_change = on_change

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Category
        ctk.CTkLabel(self, text="Category:").grid(row=0, column=0, sticky="w", padx=5, pady=2)

        if self.force_category:
            cat_values = [self.force_category]
        elif self.allowed_categories:
            cat_values = self.allowed_categories
        else:
            cat_values = list(CATEGORIES.keys())

        self.cat_combo = ctk.CTkComboBox(self, values=cat_values, command=self._update_subcategories)
        self.cat_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        if cat_values:
            self.cat_combo.set(cat_values[0])

        # Subcategory
        ctk.CTkLabel(self, text="Subcategory:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.subcat_combo = ctk.CTkComboBox(self, values=[], command=self._update_preview)
        self.subcat_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Zone (Optional)
        ctk.CTkLabel(self, text="Zone (Opt):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.zone_combo = ctk.CTkComboBox(self, values=ZONES, command=self._update_preview)
        self.zone_combo.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.zone_combo.set("")

        # Faction (Optional)
        ctk.CTkLabel(self, text="Faction (Opt):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.faction_combo = ctk.CTkComboBox(self, values=FACTIONS, command=self._update_preview)
        self.faction_combo.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.faction_combo.set("")

        # Name
        ctk.CTkLabel(self, text="Name:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=4, column=1, sticky="we", padx=5, pady=2)
        self.name_entry.bind("<KeyRelease>", self._update_preview)

        # Live Preview
        ctk.CTkLabel(self, text="Live ID:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.preview_label = ctk.CTkLabel(self, text="", text_color="green", font=("Arial", 12, "bold"))
        self.preview_label.grid(row=5, column=1, sticky="w", padx=5, pady=2)

        self._update_subcategories(self.cat_combo.get())

    def _update_subcategories(self, choice=None):
        cat = self.cat_combo.get()
        subcats = CATEGORIES.get(cat, [])
        self.subcat_combo.configure(values=subcats)
        if subcats:
            self.subcat_combo.set(subcats[0])
        else:
            self.subcat_combo.set("")
        self._update_preview()

    def _update_preview(self, event=None):
        preview = self.generate_id()
        self.preview_label.configure(text=preview)
        # Avoid firing on_change if taxonomy_generator isn't fully bound in parent yet
        if hasattr(self, 'cat_combo') and self.on_change:
            # We also wrap in try/except because parent might not have fully initialized its fields
            try:
                self.on_change()
            except AttributeError:
                pass

    def generate_id(self):
        parts = []

        cat = self.cat_combo.get()
        if cat: parts.append(cat)

        subcat = self.subcat_combo.get()
        if subcat: parts.append(subcat)

        zone = self.zone_combo.get()
        if zone: parts.append(zone)

        faction = self.faction_combo.get()
        if faction: parts.append(faction)

        name = self.name_entry.get().strip()
        if name: parts.append(name)

        raw_id = "_".join(parts)
        return sanitize_id(raw_id)

    def get_data(self):
        return {
            "category": self.cat_combo.get(),
            "subcategory": self.subcat_combo.get(),
            "zone": self.zone_combo.get(),
            "faction": self.faction_combo.get(),
            "base_name": self.name_entry.get().strip(),
            "generated_id": self.generate_id()
        }

    def load_data(self, data):
        if not data:
            self.clear_form()
            return

        if self.force_category:
            self.cat_combo.set(self.force_category)
        else:
            self.cat_combo.set(data.get("category", "material"))

        self._update_subcategories()

        subcat = data.get("subcategory", "")
        if subcat in CATEGORIES.get(self.cat_combo.get(), []):
            self.subcat_combo.set(subcat)

        self.zone_combo.set(data.get("zone", ""))
        self.faction_combo.set(data.get("faction", ""))

        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, data.get("base_name", ""))

        self._update_preview()

    def clear_form(self):
        if self.force_category:
            self.cat_combo.set(self.force_category)
        else:
            self.cat_combo.set("material")

        self._update_subcategories()
        self.zone_combo.set("")
        self.faction_combo.set("")
        self.name_entry.delete(0, 'end')
        self._update_preview()
