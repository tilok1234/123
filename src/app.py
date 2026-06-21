import customtkinter as ctk
from src.state.app_state import AppState
from src.services.storage_service import load_data
from src.ui.main_window import MainWindow

def run_app():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    state = AppState()
    load_data(state)

    app = MainWindow(state)
    app.mainloop()
