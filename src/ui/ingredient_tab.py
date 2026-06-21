import customtkinter as ctk
from src.ui.components.shared_widgets import create_labeled_entry
from src.ui.components.taxonomy_generator import TaxonomyGenerator
from src.ui.components.tooltip_preview import TooltipPreview
from src.ui.dialogs import show_error, show_info, ask_yes_no
from src.services.validation_service import sanitize_id, validate_ingredient
from src.services.dependency_service import is_ingredient_in_use
from src.services.storage_service import save_ingredients
from src.state.taxonomy import CATEGORIES

class IngredientTab(ctk.CTkFrame):
    def __init__(self, master, state, on_ingredients_changed=None, **kwargs):
        super().__init__(master, **kwargs)
        self.state = state
        self.on_ingredients_changed = on_ingredients_changed
        self.current_editing_id = None

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_preview_panel()
        self.setup_form_panel()
        self.setup_list_panel()

        self.refresh_list()

    def setup_form_panel(self):
        self.form_scroll = ctk.CTkScrollableFrame(self)
        self.form_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.form_scroll, text="Ingredient Details", font=("Arial", 16, "bold")).pack(pady=10)

        allowed = [k for k in CATEGORIES.keys() if k not in ["weapon", "gear", "pet", "recipe"]]
        self.taxonomy = TaxonomyGenerator(
            self.form_scroll,
            allowed_categories=allowed,
            on_change=self.update_preview
        )
        self.taxonomy.pack(fill="x", padx=10, pady=5)

        props_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        props_frame.pack(fill="x", padx=10, pady=5)

        self.name_entry = create_labeled_entry(props_frame, "Display Name:", 0, 0)
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        self.value_entry = create_labeled_entry(props_frame, "Base Value:", 1, 0, default_val="0")
        self.value_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        self.stack_entry = create_labeled_entry(props_frame, "Max Stack:", 2, 0, default_val="99")

        btn_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="New", command=self.clear_form, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clone", command=self.clone_ingredient, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_ingredient, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", command=self.delete_ingredient, width=80, fg_color="red", hover_color="darkred").pack(side="left", padx=5)

    def setup_preview_panel(self):
        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        ctk.CTkLabel(preview_frame, text="Tooltip Preview", font=("Arial", 16, "bold")).pack(pady=10)
        self.tooltip = TooltipPreview(preview_frame)
        self.tooltip.pack(pady=5)

    def _build_data_dict(self):
        taxonomy_data = self.taxonomy.get_data()
        return {
            "display_name": self.name_entry.get().strip(),
            "taxonomy": taxonomy_data,
            "base_value": self.value_entry.get().strip(),
            "max_stack": self.stack_entry.get().strip()
        }

    def update_preview(self):
        data = self._build_data_dict()
        self.tooltip.update_preview(data)

    def setup_list_panel(self):
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.list_frame, text="Ingredients Library", font=("Arial", 16, "bold")).pack(pady=10)

        self.listbox = ctk.CTkScrollableFrame(self.list_frame)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.list_buttons = []

    def clone_ingredient(self):
        if not self.current_editing_id:
            show_warning("No Selection", "Select an ingredient to clone first.")
            return

        self.current_editing_id = None
        current_name = self.name_entry.get()
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, f"{current_name} Copy")
        self.update_preview()
        show_info("Cloned", "Ingredient cloned. Edit the name and click Save to create a new entry.")

    def clear_form(self):
        self.current_editing_id = None
        self.taxonomy.clear_form()
        self.name_entry.delete(0, 'end')
        self.value_entry.delete(0, 'end')
        self.value_entry.insert(0, "0")
        self.stack_entry.delete(0, 'end')
        self.stack_entry.insert(0, "99")
        self.update_preview()

    def load_into_form(self, ingredient_id):
        data = self.state.ingredient_library.get(ingredient_id)
        if not data: return

        self.clear_form()
        self.current_editing_id = ingredient_id

        self.taxonomy.load_data(data.get("taxonomy", {}))
        self.name_entry.insert(0, data.get("display_name", ""))

        self.value_entry.delete(0, 'end')
        self.value_entry.insert(0, str(data.get("base_value", 0)))

        self.stack_entry.delete(0, 'end')
        self.stack_entry.insert(0, str(data.get("max_stack", 99)))
        self.update_preview()

    def refresh_list(self):
        for btn in self.list_buttons:
            btn.destroy()
        self.list_buttons.clear()

        for ing_id, data in sorted(self.state.ingredient_library.items()):
            display_name = data.get("display_name", ing_id)
            btn = ctk.CTkButton(self.listbox, text=f"{display_name} ({ing_id})",
                                anchor="w", fg_color="transparent", text_color=("black", "white"),
                                command=lambda i=ing_id: self.load_into_form(i))
            btn.pack(fill="x", pady=2)
            self.list_buttons.append(btn)

    def save_ingredient(self):
        data = self._build_data_dict()
        ingredient_id = data["taxonomy"]["generated_id"]

        is_valid, error_msg = validate_ingredient(ingredient_id, data, self.state, self.current_editing_id)

        if not is_valid:
            show_error("Validation Error", error_msg)
            return

        # If ID changed, we might need to delete old one if not in use, or warn.
        # For simplicity in V1, just treat as new if ID changes and warn about orphan.
        if self.current_editing_id and self.current_editing_id != ingredient_id:
            in_use, recipes = is_ingredient_in_use(self.current_editing_id, self.state.recipe_library)
            if in_use:
                show_error("Cannot change ID", f"Cannot rename ID. Old ID '{self.current_editing_id}' is in use by recipes: {', '.join(recipes)}")
                return
            del self.state.ingredient_library[self.current_editing_id]

        self.state.ingredient_library[ingredient_id] = data
        self.current_editing_id = ingredient_id

        save_ingredients(self.state)
        self.refresh_list()

        if self.on_ingredients_changed:
            self.on_ingredients_changed()

        show_info("Saved", f"Ingredient '{ingredient_id}' saved.")

    def delete_ingredient(self):
        if not self.current_editing_id:
            show_warning("No Selection", "Select an ingredient to delete.")
            return

        in_use, recipes = is_ingredient_in_use(self.current_editing_id, self.state.recipe_library)
        if in_use:
            show_error("Cannot Delete", f"Ingredient '{self.current_editing_id}' is used in recipes:\n{', '.join(recipes)}")
            return

        if ask_yes_no("Confirm Delete", f"Delete ingredient '{self.current_editing_id}'?"):
            del self.state.ingredient_library[self.current_editing_id]
            save_ingredients(self.state)
            self.clear_form()
            self.refresh_list()

            if self.on_ingredients_changed:
                self.on_ingredients_changed()
