from src.services.dependency_service import is_ingredient_in_use

def test_is_ingredient_in_use():
    recipe_library = {
        "iron_sword": {
            "inputs": {"iron_ingot": 2, "wood": 1},
            "outputs": {"iron_sword_item": 1}
        }
    }

    in_use, recipes = is_ingredient_in_use("wood", recipe_library)
    assert in_use == True
    assert "iron_sword" in recipes

    in_use, recipes = is_ingredient_in_use("stone", recipe_library)
    assert in_use == False
    assert len(recipes) == 0

    in_use, recipes = is_ingredient_in_use("iron_sword_item", recipe_library)
    assert in_use == True
    assert "iron_sword" in recipes
