import customtkinter as ctk
from src.ui.components.shared_widgets import create_labeled_entry
from src.ui.components.taxonomy_generator import TaxonomyGenerator
from src.ui.components.tooltip_preview import TooltipPreview
from src.ui.dialogs import show_error, show_info, ask_yes_no
from src.services.validation_service import validate_equipment
from src.services.dependency_service import is_item_in_use
from src.services.storage_service import save_equipment

class EquipmentTab(ctk.CTkFrame):
    def __init__(self, master, state, on_equipment_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state
        self.on_equipment_changed = on_equipment_changed
        self.current_editing_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0) # Tooltip
        self.grid_columnconfigure(2, weight=1) # List
        self.grid_rowconfigure(0, weight=1)

        self.setup_preview_panel()
        self.setup_form_panel()
        self.setup_list_panel()

        self.refresh_list()

    def setup_form_panel(self):
        self.form_scroll = ctk.CTkScrollableFrame(self)
        self.form_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.form_scroll, text="Equipment Details", font=("Arial", 16, "bold")).pack(pady=10)

        self.taxonomy = TaxonomyGenerator(
            self.form_scroll,
            allowed_categories=["weapon", "gear", "pet"],
            on_change=self.update_preview
        )
        self.taxonomy.pack(fill="x", padx=10, pady=5)

        props_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        props_frame.pack(fill="x", padx=10, pady=5)

        self.name_entry = create_labeled_entry(props_frame, "Display Name:", 0, 0)
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # Stats
        stats_frame = ctk.CTkFrame(self.form_scroll)
        stats_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(stats_frame, text="Base Stats", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

        self.stat_entries = {}
        row = 1
        col = 0
        for stat in ["str", "hp", "dex", "atk", "vit", "spd"]:
            entry = create_labeled_entry(stats_frame, f"{stat.upper()}:", row, col, default_val="0", width=80)
            entry.bind("<KeyRelease>", lambda e: self.update_preview())
            self.stat_entries[stat] = entry
            col += 2
            if col >= 4:
                col = 0
                row += 1

        # Weapon Specific
        self.weapon_frame = ctk.CTkFrame(self.form_scroll)
        # We will pack this dynamically if category is weapon, but pack it anyway for now to keep it simple,
        # or we can hide it. Let's just pack it.
        self.weapon_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.weapon_frame, text="Weapon Specifics", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

        for i, stat in enumerate(["dmg", "cooldown", "range"]):
            entry = create_labeled_entry(self.weapon_frame, f"{stat.capitalize()}:", 1 + (i//2), (i%2)*2, default_val="0", width=80)
            entry.bind("<KeyRelease>", lambda e: self.update_preview())
            self.stat_entries[stat] = entry

        self.proj_pattern_entry = create_labeled_entry(self.weapon_frame, "Proj. Pattern:", 3, 0, width=150)
        self.proj_pattern_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        self.stat_entries["projectile_pattern"] = self.proj_pattern_entry

        btn_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="New", command=self.clear_form, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clone", command=self.clone_equipment, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_equipment, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", command=self.delete_equipment, width=80, fg_color="red", hover_color="darkred").pack(side="left", padx=5)

    def setup_preview_panel(self):
        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        ctk.CTkLabel(preview_frame, text="Tooltip Preview", font=("Arial", 16, "bold")).pack(pady=10)
        self.tooltip = TooltipPreview(preview_frame)
        self.tooltip.pack(pady=5)

    def setup_list_panel(self):
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.list_frame, text="Equipment Library", font=("Arial", 16, "bold")).pack(pady=10)

        self.listbox = ctk.CTkScrollableFrame(self.list_frame)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.list_buttons = []

    def _build_data_dict(self):
        taxonomy_data = self.taxonomy.get_data()

        stats = {}
        for k, v in self.stat_entries.items():
            val = v.get().strip()
            if val:
                stats[k] = val

        return {
            "display_name": self.name_entry.get().strip(),
            "taxonomy": taxonomy_data,
            "stats": stats
        }

    def update_preview(self):
        data = self._build_data_dict()
        self.tooltip.update_preview(data)

    def clone_equipment(self):
        if not self.current_editing_id:
            show_warning("No Selection", "Select equipment to clone first.")
            return

        self.current_editing_id = None
        current_name = self.name_entry.get()
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, f"{current_name} Copy")
        self.update_preview()
        show_info("Cloned", "Equipment cloned. Edit the name and click Save to create a new entry.")

    def clear_form(self):
        self.current_editing_id = None
        self.taxonomy.clear_form()
        self.name_entry.delete(0, 'end')

        for k, entry in self.stat_entries.items():
            entry.delete(0, 'end')
            if k != "projectile_pattern":
                entry.insert(0, "0")

        self.update_preview()

    def load_into_form(self, equip_id):
        data = self.state.equipment_library.get(equip_id)
        if not data: return

        self.clear_form()
        self.current_editing_id = equip_id

        self.taxonomy.load_data(data.get("taxonomy", {}))
        self.name_entry.insert(0, data.get("display_name", ""))

        stats = data.get("stats", {})
        for k, entry in self.stat_entries.items():
            entry.delete(0, 'end')
            val = stats.get(k, "0" if k != "projectile_pattern" else "")
            entry.insert(0, str(val))

        self.update_preview()

    def refresh_list(self):
        for btn in self.list_buttons:
            btn.destroy()
        self.list_buttons.clear()

        for eq_id, data in sorted(self.state.equipment_library.items()):
            display_name = data.get("display_name", eq_id)
            btn = ctk.CTkButton(self.listbox, text=f"{display_name} ({eq_id})",
                                anchor="w", fg_color="transparent", text_color=("black", "white"),
                                command=lambda i=eq_id: self.load_into_form(i))
            btn.pack(fill="x", pady=2)
            self.list_buttons.append(btn)

    def save_equipment(self):
        data = self._build_data_dict()
        equip_id = data["taxonomy"]["generated_id"]

        is_valid, error_msg = validate_equipment(equip_id, data, self.state, self.current_editing_id)

        if not is_valid:
            show_error("Validation Error", error_msg)
            return

        if self.current_editing_id and self.current_editing_id != equip_id:
            in_use, recipes = is_item_in_use(self.current_editing_id, self.state.recipe_library)
            if in_use:
                show_error("Cannot change ID", f"Cannot rename ID. Old ID '{self.current_editing_id}' is in use by recipes: {', '.join(recipes)}")
                return
            del self.state.equipment_library[self.current_editing_id]

        self.state.equipment_library[equip_id] = data
        self.current_editing_id = equip_id

        save_equipment(self.state)
        self.refresh_list()
        self.update_preview()

        if self.on_equipment_changed:
            self.on_equipment_changed()

        show_info("Saved", f"Equipment '{equip_id}' saved.")

    def delete_equipment(self):
        if not self.current_editing_id:
            show_warning("No Selection", "Select equipment to delete.")
            return

        in_use, recipes = is_item_in_use(self.current_editing_id, self.state.recipe_library)
        if in_use:
            show_error("Cannot Delete", f"Equipment '{self.current_editing_id}' is used in recipes:\n{', '.join(recipes)}")
            return

        if ask_yes_no("Confirm Delete", f"Delete equipment '{self.current_editing_id}'?"):
            del self.state.equipment_library[self.current_editing_id]
            save_equipment(self.state)
            self.clear_form()
            self.refresh_list()

            if self.on_equipment_changed:
                self.on_equipment_changed()
