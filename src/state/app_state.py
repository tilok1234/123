class AppState:
    def __init__(self):
        self.ingredient_library = {}
        self.recipe_library = {}

        self.active_input_rows = []
        self.active_output_rows = []
        self.active_cost_rows = []
        self.active_tag_rows = []

        self.icon_cache = {}
