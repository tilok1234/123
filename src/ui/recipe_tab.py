import customtkinter as ctk
from src.ui.components.shared_widgets import create_labeled_entry, create_labeled_textbox
from src.ui.components.dynamic_rows import DynamicRowContainer
from src.ui.dialogs import show_error, show_info, ask_yes_no
from src.services.validation_service import sanitize_id, validate_recipe
from src.services.storage_service import save_recipes

class RecipeTab(ctk.CTkFrame):
    def __init__(self, master, state, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state
        self.current_editing_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_form_panel()
        self.setup_list_panel()
        self.refresh_list()

    def setup_form_panel(self):
        self.form_scroll = ctk.CTkScrollableFrame(self)
        self.form_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Meta
        meta_frame = ctk.CTkFrame(self.form_scroll)
        meta_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(meta_frame, text="Recipe Metadata", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        self.id_entry = create_labeled_entry(meta_frame, "Recipe ID:", 1, 0)
        self.name_entry = create_labeled_entry(meta_frame, "Recipe Name:", 2, 0)
        self.cat_entry = create_labeled_entry(meta_frame, "Category:", 3, 0, default_val="weapon")
        self.station_entry = create_labeled_entry(meta_frame, "Station:", 4, 0, default_val="forge")

        # Dynamic Rows
        self.inputs_container = DynamicRowContainer(
            self.form_scroll, self.state, "Inputs", "active_input_rows",
            self.get_ingredient_options, height=150
        )
        self.inputs_container.pack(fill="x", pady=5)

        self.outputs_container = DynamicRowContainer(
            self.form_scroll, self.state, "Outputs", "active_output_rows",
            self.get_ingredient_options, height=150
        )
        self.outputs_container.pack(fill="x", pady=5)

        # Costs and Tags (simplified dynamic rows, text-based)
        self.costs_container = DynamicRowContainer(
            self.form_scroll, self.state, "Costs (Currency)", "active_cost_rows",
            lambda: ["gold", "silver", "copper", "gems", "mana"], height=100
        )
        self.costs_container.pack(fill="x", pady=5)

        # Notes
        notes_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        notes_frame.pack(fill="x", pady=5)
        self.notes_text = create_labeled_textbox(notes_frame, "Notes:", 0, 0, width=400, height=80)

        # Buttons
        btn_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="New", command=self.clear_form, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_recipe, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", command=self.delete_recipe, width=80, fg_color="red", hover_color="darkred").pack(side="left", padx=5)

    def setup_list_panel(self):
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.list_frame, text="Recipe Library", font=("Arial", 16, "bold")).pack(pady=10)

        self.listbox = ctk.CTkScrollableFrame(self.list_frame)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.list_buttons = []

    def get_ingredient_options(self):
        return sorted(list(self.state.ingredient_library.keys()))

    def refresh_ingredient_dropdowns(self):
        self.inputs_container.refresh_options()
        self.outputs_container.refresh_options()

    def clear_form(self):
        self.current_editing_id = None
        self.id_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.cat_entry.delete(0, 'end')
        self.station_entry.delete(0, 'end')
        self.notes_text.delete("1.0", "end")

        self.inputs_container.clear_rows()
        self.outputs_container.clear_rows()
        self.costs_container.clear_rows()

    def load_into_form(self, recipe_id):
        data = self.state.recipe_library.get(recipe_id)
        if not data: return

        self.clear_form()
        self.current_editing_id = recipe_id

        self.id_entry.insert(0, recipe_id)
        self.name_entry.insert(0, data.get("name", ""))
        self.cat_entry.insert(0, data.get("category", ""))
        self.station_entry.insert(0, data.get("station", ""))

        if "notes" in data:
            self.notes_text.insert("1.0", data["notes"])

        for k, v in data.get("inputs", {}).items():
            self.inputs_container.add_row(k, v)

        for k, v in data.get("outputs", {}).items():
            self.outputs_container.add_row(k, v)

        for k, v in data.get("costs", {}).items():
            self.costs_container.add_row(k, v)

    def refresh_list(self):
        for btn in self.list_buttons:
            btn.destroy()
        self.list_buttons.clear()

        for rec_id, data in sorted(self.state.recipe_library.items()):
            display_name = data.get("name", rec_id)
            btn = ctk.CTkButton(self.listbox, text=f"{display_name} ({rec_id})",
                                anchor="w", fg_color="transparent", text_color=("black", "white"),
                                command=lambda r=rec_id: self.load_into_form(r))
            btn.pack(fill="x", pady=2)
            self.list_buttons.append(btn)

    def save_recipe(self):
        raw_id = self.id_entry.get()
        recipe_id = sanitize_id(raw_id)

        if raw_id != recipe_id:
            self.id_entry.delete(0, 'end')
            self.id_entry.insert(0, recipe_id)

        data = {
            "name": self.name_entry.get().strip(),
            "category": self.cat_entry.get().strip(),
            "station": self.station_entry.get().strip(),
            "inputs": self.inputs_container.get_data(),
            "outputs": self.outputs_container.get_data(),
            "costs": self.costs_container.get_data(),
            "notes": self.notes_text.get("1.0", "end-1c").strip()
        }

        is_valid, error_msg = validate_recipe(recipe_id, data, self.state, self.current_editing_id)

        if not is_valid:
            show_error("Validation Error", error_msg)
            return

        if self.current_editing_id and self.current_editing_id != recipe_id:
            del self.state.recipe_library[self.current_editing_id]

        self.state.recipe_library[recipe_id] = data
        self.current_editing_id = recipe_id

        save_recipes(self.state)
        self.refresh_list()

        show_info("Saved", f"Recipe '{recipe_id}' saved.")

    def delete_recipe(self):
        if not self.current_editing_id:
            show_warning("No Selection", "Select a recipe to delete.")
            return

        if ask_yes_no("Confirm Delete", f"Delete recipe '{self.current_editing_id}'?"):
            del self.state.recipe_library[self.current_editing_id]
            save_recipes(self.state)
            self.clear_form()
            self.refresh_list()
