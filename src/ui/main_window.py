import customtkinter as ctk
from src.ui.ingredient_tab import IngredientTab
from src.ui.recipe_tab import RecipeTab
from src.services.export_service import export_data
from src.ui.dialogs import show_info, show_error

class MainWindow(ctk.CTk):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state

        self.title("Crafting Recipe Creator")
        self.geometry("1000x700")

        # Tools / Header frame
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.header_frame, text="Crafting Recipe Manager", font=("Arial", 20, "bold")).pack(side="left", padx=10)

        # Export button
        ctk.CTkButton(self.header_frame, text="Export JSON", command=self.do_export, fg_color="green", hover_color="darkgreen").pack(side="right", padx=10)

        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabview.add("Ingredients")
        self.tabview.add("Recipes")

        # Add Tabs
        self.ingredient_tab = IngredientTab(self.tabview.tab("Ingredients"), self.app_state, on_ingredients_changed=self.on_ingredients_changed)
        self.ingredient_tab.pack(fill="both", expand=True)

        self.recipe_tab = RecipeTab(self.tabview.tab("Recipes"), self.app_state)
        self.recipe_tab.pack(fill="both", expand=True)

    def on_ingredients_changed(self):
        # Refresh the recipe tab dropdowns when ingredients change
        self.recipe_tab.refresh_ingredient_dropdowns()

    def do_export(self):
        success, msg = export_data(self.app_state)
        if success:
            show_info("Export Complete", msg)
        else:
            show_error("Export Failed", msg)
