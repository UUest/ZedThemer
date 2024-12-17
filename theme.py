import json
import os
from rgbhex import hex_to_rgb, rgb_to_hex
from colors import RESET

def load_theme_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_theme_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)



def display_json_theme(theme_path):
    # Check if file exists
    if not os.path.exists(theme_path):
        print(f"Error: File '{theme_path}' does not exist.")
        return

    # Load JSON
    try:
        with open(theme_path, "r") as f:
            theme_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from '{theme_path}'.")
        return

    # Extract themes from the JSON
    print("\nTheme Overview:")
    print("-" * 40)
    themes = theme_data.get("themes", [])
    if not themes:
        print("No themes found in the JSON file.")
        return

    for theme in themes:
        appearance = theme.get("appearance", "unknown")
        name = theme.get("name", "Unnamed")
        print(f"Appearance: {appearance.capitalize()}, Name: {name}")
        print("-" * 40)

        # Display key-value pairs in the style dictionary
        style = theme.get("style", {})
        for key, value in style.items():
            if key == "syntax" and isinstance(value, dict):
                print(f"\nSyntax Colors:")
                print("-" * 40)
                for syntax_key, syntax_value in value.items():
                    if isinstance(syntax_value, dict) and "color" in syntax_value:
                        color_hex = syntax_value["color"]
                        if isinstance(color_hex, str) and color_hex.startswith("#"):
                            try:
                                rgb = hex_to_rgb(color_hex)
                                color_block = f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m  {RESET}"
                                print(f"{color_block} {color_hex} - {syntax_key}")
                            except ValueError:
                                print(f"Invalid color value for {syntax_key}: {color_hex}")
                        else:
                            print(f"{syntax_key}: {color_hex}")
                    else:
                        print(f"{syntax_key}: {syntax_value}")
                print("-" * 40)
            elif isinstance(value, str) and value.startswith("#"):
                try:
                    rgb = hex_to_rgb(value)
                    color_block = f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m  {RESET}"
                    print(f"{color_block} {value} - {key}")
                except ValueError:
                    print(f"Invalid color value for {key}: {value}")
            else:
                print(f"{key}: {value}")
        print("-" * 40)
