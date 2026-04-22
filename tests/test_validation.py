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
    state.equipment_library = {}
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
    state.equipment_library = {}
    data = {
        "name": "Iron Sword",
        "category": "weapon",
        "station": "forge",
        "inputs": {"iron": "2"}
    }
    is_valid, msg = validate_recipe("iron_sword", data, state)
    assert is_valid == False
    assert "does not exist" in msg

def test_validate_equipment():
    from src.services.validation_service import validate_equipment
    state = AppState()

    # Valid equipment
    data = {
        "display_name": "Test Sword",
        "taxonomy": {"category": "weapon"},
        "stats": {"str": 10, "dmg": 50, "range": 1.5, "cooldown": 0.8}
    }
    is_valid, msg = validate_equipment("weapon_sword_test", data, state)
    assert is_valid == True

    # Invalid equipment (negative string)
    data["stats"]["str"] = -5
    is_valid, msg = validate_equipment("weapon_sword_test", data, state)
    assert is_valid == False
    assert "STR must be >= 0" in msg
