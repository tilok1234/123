import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
EXPORT_DIR = os.path.join(BASE_DIR, "export")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

INGREDIENTS_MASTER = os.path.join(DATA_DIR, "ingredients_master.json")
RECIPES_MASTER = os.path.join(DATA_DIR, "recipes_master.json")
EQUIPMENT_MASTER = os.path.join(DATA_DIR, "equipment_master.json")

INGREDIENTS_EXPORT = os.path.join(EXPORT_DIR, "ingredients_export.json")
RECIPES_EXPORT = os.path.join(EXPORT_DIR, "recipes_export.json")
EQUIPMENT_EXPORT = os.path.join(EXPORT_DIR, "equipment_export.json")
