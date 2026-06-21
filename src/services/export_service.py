import os
from src.config import INGREDIENTS_EXPORT, RECIPES_EXPORT, EQUIPMENT_EXPORT
from src.services.storage_service import save_json

def export_data(state):
    # Here you might want to convert the dictionaries into Godot's specific format
    # For now, it just saves a copy in the export dir
    save_json(INGREDIENTS_EXPORT, state.ingredient_library)
    save_json(EQUIPMENT_EXPORT, state.equipment_library)
    save_json(RECIPES_EXPORT, state.recipe_library)

    return True, "Data exported successfully"
