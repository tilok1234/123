from PIL import Image
import customtkinter as ctk
import os
from src.config import ASSETS_DIR

def load_icon(state, icon_name, size=(20, 20)):
    icon_path = os.path.join(ASSETS_DIR, "icons", f"{icon_name}.png")

    # Check if icon exists, if not, return None (or a default placeholder)
    if not os.path.exists(icon_path):
        return None

    cache_key = f"{icon_name}_{size[0]}x{size[1]}"

    if cache_key not in state.icon_cache:
        image = Image.open(icon_path)
        icon = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        state.icon_cache[cache_key] = icon

    return state.icon_cache[cache_key]
