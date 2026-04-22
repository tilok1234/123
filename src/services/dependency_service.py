def is_item_in_use(item_id, recipe_library):
    recipes_using_item = []

    for recipe_id, recipe_data in recipe_library.items():
        if item_id in recipe_data.get("inputs", {}):
            recipes_using_item.append(recipe_id)
            continue

        if item_id in recipe_data.get("outputs", {}):
            recipes_using_item.append(recipe_id)
            continue

    return len(recipes_using_item) > 0, recipes_using_item

# Keep for backwards compatibility with ingredient_tab.py temporarily or refactor callers
is_ingredient_in_use = is_item_in_use
