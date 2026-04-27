import tkinter as tk
from tkinter import ttk
import keyboard
import pyperclip
import time
import json
import os

CONFIG_FILE = "config.json"

class QueueExpanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Absurdum32 Prompt Queue Pad v6")
        self.root.geometry("800x600")

        self.profiles = {} # Maps keyphrase to prompt pad text
        self.active_hooks = [] # Store hooks to clean them up if needed

        # Top Frame for Tabs and Actions
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.top_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Profiles / Keybinds
        self.profiles_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profiles_tab, text="Profiles & Keybinds")

        self.setup_profiles_tab()

        # Tab 2: Prompt Library Queue
        self.queue_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.queue_tab, text="Prompt Library Queue")

        self.setup_queue_tab()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Type a keyphrase to trigger | Ctrl+S saves active tab")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load existing config
        self.load_config()

        # Bind save hotkey
        self.root.bind('<Control-s>', lambda e: self.save_all())

        # Register hooks for profiles
        self.register_all_hooks()

    def setup_profiles_tab(self):
        # Left pane for list of profiles
        self.paned = ttk.PanedWindow(self.profiles_tab, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.list_frame = ttk.Frame(self.paned)
        self.paned.add(self.list_frame, weight=1)

        self.profile_listbox = tk.Listbox(self.list_frame)
        self.profile_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.profile_listbox.bind('<<ListboxSelect>>', self.on_profile_select)

        self.list_scroll = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.profile_listbox.yview)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.profile_listbox.config(yscrollcommand=self.list_scroll.set)

        self.list_btn_frame = ttk.Frame(self.list_frame)
        self.list_btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.add_btn = ttk.Button(self.list_btn_frame, text="Add New", command=self.add_profile)
        self.add_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.del_btn = ttk.Button(self.list_btn_frame, text="Delete", command=self.delete_profile)
        self.del_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Right pane for editing profile
        self.edit_frame = ttk.Frame(self.paned)
        self.paned.add(self.edit_frame, weight=3)

        ttk.Label(self.edit_frame, text="Keyphrase (e.g., |keybind1):").pack(anchor=tk.W)
        self.keyphrase_var = tk.StringVar()
        self.keyphrase_entry = ttk.Entry(self.edit_frame, textvariable=self.keyphrase_var)
        self.keyphrase_entry.pack(fill=tk.X, pady=2)

        # Track previous keyphrase for renaming
        self.current_editing_keyphrase = None
        self.keyphrase_var.trace_add('write', self.on_keyphrase_change)

        ttk.Label(self.edit_frame, text="Prompt Pad Text:").pack(anchor=tk.W, pady=(10, 0))
        self.pad_text = tk.Text(self.edit_frame, wrap=tk.WORD)
        self.pad_text.pack(fill=tk.BOTH, expand=True)
        self.pad_text.bind('<KeyRelease>', self.on_pad_text_change)

        self.save_profiles_btn = ttk.Button(self.edit_frame, text="Save All Profiles", command=self.save_all)
        self.save_profiles_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def setup_queue_tab(self):
        self.queue_controls_frame = ttk.Frame(self.queue_tab)
        self.queue_controls_frame.pack(fill=tk.X, padx=5, pady=5)

        self.save_queue_btn = ttk.Button(self.queue_controls_frame, text="Save Queue", command=self.save_all)
        self.save_queue_btn.pack(side=tk.LEFT)

        self.queue_text = tk.Text(self.queue_tab, wrap=tk.NONE)

        # Add scrollbars to queue text
        self.queue_scroll_y = ttk.Scrollbar(self.queue_tab, orient=tk.VERTICAL, command=self.queue_text.yview)
        self.queue_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_scroll_x = ttk.Scrollbar(self.queue_tab, orient=tk.HORIZONTAL, command=self.queue_text.xview)
        self.queue_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.queue_text.configure(yscrollcommand=self.queue_scroll_y.set, xscrollcommand=self.queue_scroll_x.set)

        self.queue_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def add_profile(self):
        new_key = f"|new_keybind_{len(self.profiles) + 1}"
        self.profiles[new_key] = "Enter your prompt pad text here..."
        self.update_profile_listbox()
        # Select the newly added profile
        idx = self.profile_listbox.get(0, tk.END).index(new_key)
        self.profile_listbox.selection_clear(0, tk.END)
        self.profile_listbox.selection_set(idx)
        self.on_profile_select(None)

        self.register_all_hooks()

    def delete_profile(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
        key = self.profile_listbox.get(selection[0])
        if key in self.profiles:
            del self.profiles[key]
        self.update_profile_listbox()

        # Clear edit frame
        self.current_editing_keyphrase = None
        self.keyphrase_var.set("")
        self.pad_text.delete("1.0", tk.END)

        self.register_all_hooks()

    def update_profile_listbox(self):
        self.profile_listbox.delete(0, tk.END)
        for key in self.profiles:
            self.profile_listbox.insert(tk.END, key)

    def on_profile_select(self, event):
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        key = self.profile_listbox.get(selection[0])
        self.current_editing_keyphrase = key

        # Populate edit frame
        self.keyphrase_var.set(key)
        self.pad_text.delete("1.0", tk.END)
        self.pad_text.insert("1.0", self.profiles[key])

    def on_keyphrase_change(self, *args):
        if self.current_editing_keyphrase is None:
            return

        new_key = self.keyphrase_var.get()
        old_key = self.current_editing_keyphrase

        if new_key != old_key and new_key:
            # Rename in dict
            self.profiles[new_key] = self.profiles.pop(old_key)
            self.current_editing_keyphrase = new_key

            # Update listbox text without changing selection
            selection = self.profile_listbox.curselection()
            if selection:
                idx = selection[0]
                self.profile_listbox.delete(idx)
                self.profile_listbox.insert(idx, new_key)
                self.profile_listbox.selection_set(idx)

            self.register_all_hooks()

    def on_pad_text_change(self, event):
        if self.current_editing_keyphrase:
            self.profiles[self.current_editing_keyphrase] = self.pad_text.get("1.0", tk.END).strip()

    def register_all_hooks(self):
        # Clear existing hooks
        keyboard.unhook_all()
        self.active_hooks.clear()

        # Register new word hooks for each profile keyphrase
        for keyphrase in self.profiles.keys():
            if not keyphrase:
                continue

            # Use keyboard.add_word_listener to listen for exact phrases
            # We wrap trigger_paste in a lambda to pass the keyphrase
            # triggers_on_space=False means it triggers immediately upon typing the last character
            hook = keyboard.add_abbreviation(keyphrase, "") # We use abbreviation to swallow the text, but handle logic ourselves

            # Using add_word_listener is safer, but doesn't backspace.
            # We will use on_word to detect it, and manually backspace.
            # But wait, keyboard.add_word_listener lets us pass a callback
            # We need to swallow the keyphrase.
            pass

        # We'll use a better approach: hook all keystrokes and buffer them
        self.setup_typing_buffer()

    def setup_typing_buffer(self):
        keyboard.unhook_all()
        # Instead of keyboard.add_word_listener which might be finicky,
        # we can use keyboard.on_release to track typed characters.
        # But actually, keyboard.add_abbreviation is designed exactly for this: typing |key1 replaces it.
        # But we want dynamic replacement.

        for keyphrase in self.profiles.keys():
            if not keyphrase:
                continue

            # For each keyphrase, we want to listen for it being typed.
            # We can use add_word_listener.
            cb = self.create_trigger_callback(keyphrase)
            # Add word listener triggers when the word is typed followed by space or enter
            # To trigger immediately without space, we can just use hotkeys if it was a combo,
            # but for a phrase like "|keybind1", word listener is best.
            # Actually, keyboard.add_word_listener triggers on word boundaries.
            # Let's use keyboard.on_release to build a custom buffer for immediate triggering.
            pass

        # Custom buffer approach
        self.typing_buffer = ""
        keyboard.on_release(self.on_key_release)

    def on_key_release(self, event):
        # Only care about character keys
        if len(event.name) == 1:
            self.typing_buffer += event.name
        elif event.name == 'space':
            self.typing_buffer += ' '
        elif event.name == 'backspace':
            self.typing_buffer = self.typing_buffer[:-1]
        elif event.name == 'enter':
            self.typing_buffer = "" # reset on enter usually? Or maybe not. Let's just keep last N chars.

        # Keep buffer small
        if len(self.typing_buffer) > 50:
            self.typing_buffer = self.typing_buffer[-50:]

        # Check if any keyphrase is at the end of the buffer
        for keyphrase in self.profiles.keys():
            if keyphrase and self.typing_buffer.endswith(keyphrase):
                # Trigger found!
                self.typing_buffer = "" # reset

                # Erase the typed keyphrase using backspaces
                for _ in range(len(keyphrase)):
                    keyboard.send('backspace')
                    time.sleep(0.01)

                # We need to use after to ensure thread safety with tkinter
                self.root.after(0, self._process_paste, keyphrase)
                break

    def create_trigger_callback(self, keyphrase):
        def callback():
            self.root.after(0, self._process_paste, keyphrase)
        return callback

    def _process_paste(self, keyphrase):
        # 1. Get the first line from the queue
        queue_content = self.queue_text.get("1.0", tk.END)
        lines = queue_content.splitlines()

        if not lines or all(not line.strip() for line in lines):
            self.status_var.set("Queue is empty.")
            return

        first_line = lines[0]
        remaining_lines = lines[1:]

        # 2. Prepare the payload
        payload = ""
        pad_content = self.profiles.get(keyphrase, "").strip()
        if pad_content:
            payload += pad_content + "\n\n"

        payload += first_line

        # 3. Update the queue (destructive read)
        # Clear the queue and insert the remaining lines
        self.queue_text.delete("1.0", tk.END)
        if remaining_lines:
            self.queue_text.insert("1.0", "\n".join(remaining_lines))

        # 4. Copy to clipboard and paste
        pyperclip.copy(payload)

        # Give a small delay to ensure clipboard is updated
        time.sleep(0.1)
        keyboard.send('ctrl+v')

        self.status_var.set(f"Triggered by {keyphrase}. Queue entry deleted. Paste attempted.")

        # Automatically save after modifying queue
        self.save_all()

    def save_all(self):
        config = {
            "profiles": self.profiles,
            "queue_text": self.queue_text.get("1.0", tk.END).strip()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        self.status_var.set("Configuration saved successfully.")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)

                # Load profiles
                if "profiles" in config:
                    self.profiles = config["profiles"]
                else:
                    # Migration from old format if exists
                    pad_text = config.get("pad_text", "")
                    if pad_text:
                        self.profiles["|default"] = pad_text

                self.update_profile_listbox()
                if self.profiles:
                    self.profile_listbox.selection_set(0)
                    self.on_profile_select(None)

                # Load queue
                queue_text = config.get("queue_text", "")
                if queue_text:
                    self.queue_text.delete("1.0", tk.END)
                    self.queue_text.insert("1.0", queue_text)

            except Exception as e:
                self.status_var.set(f"Error loading config: {e}")
        else:
            # Default profiles
            self.profiles = {
                "|keybind1": "First standard prompt pad text...",
                "|keybind2": "Second standard prompt pad text..."
            }
            self.update_profile_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueExpanderApp(root)
    root.mainloop()
