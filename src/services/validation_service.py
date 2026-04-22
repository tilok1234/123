import re

def sanitize_id(id_str):
    return re.sub(r'[^a-z0-9_]', '', id_str.lower().strip().replace(' ', '_'))

def validate_ingredient(ingredient_id, data, state, original_id=None):
    if not ingredient_id:
        return False, "ID cannot be empty."
    if not data.get("display_name"):
        return False, "Display name cannot be empty."

    try:
        base_value = int(data.get("base_value", 0))
        if base_value < 0:
            return False, "Base value must be >= 0."
        data["base_value"] = base_value
    except ValueError:
        return False, "Base value must be an integer."

    try:
        max_stack = int(data.get("max_stack", 1))
        if max_stack <= 0:
            return False, "Max stack must be > 0."
        data["max_stack"] = max_stack
    except ValueError:
        return False, "Max stack must be an integer."

    if ingredient_id != original_id and ingredient_id in state.ingredient_library:
        return False, f"Ingredient ID '{ingredient_id}' already exists."

    return True, ""

def validate_recipe(recipe_id, data, state, original_id=None):
    if not recipe_id:
        return False, "Recipe ID cannot be empty."
    if not data.get("name"):
        return False, "Recipe name cannot be empty."
    if not data.get("category"):
        return False, "Category cannot be empty."
    if not data.get("station"):
        return False, "Station cannot be empty."

    if recipe_id != original_id and recipe_id in state.recipe_library:
        return False, f"Recipe ID '{recipe_id}' already exists."

    # Validate inputs
    for ing_id, qty in data.get("inputs", {}).items():
        if ing_id not in state.ingredient_library:
            return False, f"Input ingredient '{ing_id}' does not exist."
        try:
            qty = int(qty)
            if qty <= 0:
                return False, f"Input quantity for '{ing_id}' must be > 0."
            data["inputs"][ing_id] = qty
        except ValueError:
            return False, f"Input quantity for '{ing_id}' must be an integer."

    # Validate outputs
    for ing_id, qty in data.get("outputs", {}).items():
        if ing_id not in state.ingredient_library:
            return False, f"Output item '{ing_id}' does not exist."
        try:
            qty = int(qty)
            if qty <= 0:
                return False, f"Output quantity for '{ing_id}' must be > 0."
            data["outputs"][ing_id] = qty
        except ValueError:
            return False, f"Output quantity for '{ing_id}' must be an integer."

    # Validate costs
    for currency, cost in data.get("costs", {}).items():
        try:
            cost = int(cost)
            if cost < 0:
                return False, f"Cost for '{currency}' must be >= 0."
            data["costs"][currency] = cost
        except ValueError:
            return False, f"Cost for '{currency}' must be an integer."

    return True, ""
