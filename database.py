import json
import os
from tkinter import messagebox

DATABASE_FILE = 'database.json'

def load_database():
    """Carica il database JSON dal file."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Errore", "Il file database.json è corrotto.")
                return {}
    else:
        return {}

def save_database(data):
    """Salva il database JSON nel file."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)