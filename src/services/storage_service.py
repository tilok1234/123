import json
import os
from src.config import INGREDIENTS_MASTER, RECIPES_MASTER, EQUIPMENT_MASTER

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)

def load_data(state):
    state.ingredient_library = load_json(INGREDIENTS_MASTER)
    state.equipment_library = load_json(EQUIPMENT_MASTER)
    state.recipe_library = load_json(RECIPES_MASTER)

def save_ingredients(state):
    save_json(INGREDIENTS_MASTER, state.ingredient_library)

def save_equipment(state):
    save_json(EQUIPMENT_MASTER, state.equipment_library)

def save_recipes(state):
    save_json(RECIPES_MASTER, state.recipe_library)
