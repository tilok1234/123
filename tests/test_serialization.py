import os
import json
from src.state.app_state import AppState
from src.services.storage_service import save_json, load_json
from src.services.export_service import export_data
from src.config import INGREDIENTS_EXPORT, RECIPES_EXPORT

def test_save_load_json(tmpdir):
    filepath = os.path.join(tmpdir, "test.json")
    data = {"test_key": "test_value", "number": 42}

    save_json(filepath, data)
    assert os.path.exists(filepath)

    loaded = load_json(filepath)
    assert loaded == data

def test_export_data():
    state = AppState()
    state.ingredient_library = {"test_ing": {"display_name": "Test"}}
    state.recipe_library = {"test_rec": {"name": "Test Recipe"}}

    success, msg = export_data(state)
    assert success == True

    assert os.path.exists(INGREDIENTS_EXPORT)
    assert os.path.exists(RECIPES_EXPORT)

    # Cleanup
    os.remove(INGREDIENTS_EXPORT)
    os.remove(RECIPES_EXPORT)
