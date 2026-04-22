def is_ingredient_in_use(ingredient_id, recipe_library):
    recipes_using_ingredient = []

    for recipe_id, recipe_data in recipe_library.items():
        if ingredient_id in recipe_data.get("inputs", {}):
            recipes_using_ingredient.append(recipe_id)
            continue

        if ingredient_id in recipe_data.get("outputs", {}):
            recipes_using_ingredient.append(recipe_id)
            continue

    return len(recipes_using_ingredient) > 0, recipes_using_ingredient
