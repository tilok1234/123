from src.services.validation_service import validate_ingredient, validate_recipe, sanitize_id
from src.state.app_state import AppState

def test_sanitize_id():
    assert sanitize_id("Iron Ingot") == "iron_ingot"
    assert sanitize_id("  WOOD_Stick 1! ") == "wood_stick_1"

def test_validate_ingredient_valid():
    state = AppState()
    data = {"display_name": "Iron Ingot", "base_value": "10", "max_stack": "99"}
    is_valid, msg = validate_ingredient("iron_ingot", data, state)
    assert is_valid == True
    assert data["base_value"] == 10  # check coercion
    assert data["max_stack"] == 99   # check coercion

def test_validate_ingredient_invalid():
    state = AppState()
    data = {"display_name": "Iron Ingot", "base_value": "-5", "max_stack": "99"}
    is_valid, msg = validate_ingredient("iron_ingot", data, state)
    assert is_valid == False
    assert ">= 0" in msg

def test_validate_recipe_valid():
    state = AppState()
    state.ingredient_library = {"iron": {}}
    data = {
        "name": "Iron Sword",
        "category": "weapon",
        "station": "forge",
        "inputs": {"iron": "2"},
        "outputs": {"iron": "1"}
    }
    is_valid, msg = validate_recipe("iron_sword", data, state)
    assert is_valid == True

def test_validate_recipe_missing_ingredient():
    state = AppState()
    state.ingredient_library = {}
    data = {
        "name": "Iron Sword",
        "category": "weapon",
        "station": "forge",
        "inputs": {"iron": "2"}
    }
    is_valid, msg = validate_recipe("iron_sword", data, state)
    assert is_valid == False
    assert "does not exist" in msg
