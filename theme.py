import json
import os

def load_theme_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_theme_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
