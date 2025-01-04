from logging import exception
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from colorthief import ColorThief
import json
import os
from rgbhex import rgb_to_hex, hex_to_rgb

class Zhemer:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title("Zed themer")
        self.palette = []
        self.theme_data = {}
        self.create_widgets()

    def create_widgets(self):
        # Top frame: buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        load_image_btn = tk.Button(top_frame, text="Load Image", command=self.load_image)
        load_image_btn.grid(row=0, column=0, padx=5)

        load_theme_btn = tk.Button(top_frame, text="Load Theme", command=self.load_theme_json)
        load_theme_btn.grid(row=0, column=1, padx=5)

        save_theme_btn = tk.Button(top_frame, text="Save Theme", command=self.save_theme_json)
        save_theme_btn.grid(row=0, column=3, padx=5)

        add_color_btn = tk.Button(top_frame, text="Add Color", command=self.add_color)
        add_color_btn.grid(row=0, column=4, padx=5)

        # Palette Display
        self.palette_frame = tk.Frame(self.root, relief="sunken", borderwidth=2)
        self.palette_frame.pack(pady=10, fill="both", expand=True)

        self.update_palette_display()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return

        try:
            ct = ColorThief(file_path)
            self.palette = ct.get_palette(color_count=8, quality=1)
            self.update_palette_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def load_theme_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                self.theme_data = json.load(f)
            messagebox.showinfo("Success", "Theme JSON loaded successfully!")
            self.update_palette_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme JSON: {e}")

    def save_theme_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "w") as f:
                json.dump(self.theme_data, f, indent=4)
            messagebox.showinfo("Success", "Theme saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme JSON: {e}")

    def add_color(self):
        color = colorchooser.askcolor(title="Choose a Color")
        if color[1]: # color[1] is the hex string
            self.palette.append(hex_to_rgb(color[1]))
            self.update_palette_display()

    def clear_palette(self):
        self.palette = []
        self.update_palette_display()

    def update_palette_display(self):
        # Clear the previous palette frame and create a scrollable canvas
        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(self.palette_frame, bg=self.palette_frame["bg"])
        scrollbar = tk.Scrollbar(self.palette_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.palette_frame["bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display empty message if no palette or theme data
        if not self.palette and not self.theme_data:
            empty_label = tk.Label(scrollable_frame, text="No palette or theme loaded.", font=("Arial", 12))
            empty_label.pack()
            return

        # Display theme data in the order it appears in JSON
        tk.Label(scrollable_frame, text="Theme Options:", font=("Arial", 12, "bold")).pack(anchor="w")
        style = self.theme_data.get("themes", [{}])[0].get("style", {})

        # Collect all options in order, including nested ones like syntax
        theme_items = []
        for key, value in style.items():
            if key == "syntax" and isinstance(value, dict):
                for syntax_key, syntax_value in value.items():
                    if isinstance(syntax_value, dict) and "color" in syntax_value:
                        theme_items.append((syntax_key, syntax_value.get("color")))
            else:
                theme_items.append((key, value))

        # Display each option with a button to choose a color
        for key, color_hex in theme_items:
            frame = tk.Frame(scrollable_frame, bg=self.palette_frame["bg"])
            frame.pack(fill=tk.X, pady=2, padx=5)

            # Label for the key
            label = tk.Label(
                frame,
                text=key,
                bg=self.palette_frame["bg"],
                fg="black",
                width=30,
                anchor="w"
            )
            label.pack(side="left")

            # Color block (or placeholder for no color)
            if color_hex and sanitize_hex_color(color_hex):
                color_display = tk.Label(frame, text=color_hex, bg=color_hex, fg="white", width=15, height=2)
            else:
                color_display = tk.Label(frame, text="No Color", bg=self.palette_frame["bg"], fg="black", width=15, height=2)
            color_display.pack(side="left", padx=5)

            # Button to choose a new color
            def choose_color(c_key=key, display=color_display):
                chosen_color = tk.colorchooser.askcolor()[1]
                if chosen_color:
                    display.config(text=chosen_color, bg=chosen_color)
                    self.update_theme_color(c_key, chosen_color)

            select_button = tk.Button(frame, text="Set Color", command=choose_color)
            select_button.pack(side="left", padx=5)

        # Button to clear all colors
        clear_button = tk.Button(scrollable_frame, text="Clear All Colors", command=self.clear_all_colors)
        clear_button.pack(pady=10)

    # Function to update theme data with a new color
    def update_theme_color(self, key, new_color):
        """
        Update the theme with a new color for a specific key.

        Args:
            key (str): The theme key to update.
            new_color (str): The new color value.
        """
        sanitized_color = sanitize_hex_color(new_color)
        if not sanitized_color:
            print(f"Invalid color: {new_color}")
            return

        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        if key in style:
            style[key] = sanitized_color
        elif "syntax" in style and isinstance(style["syntax"], dict):
            if key in style["syntax"]:
                style["syntax"][key]["color"] = sanitized_color
        self.update_palette_display()

    # Function to clear all colors
    def clear_all_colors(self):
        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        for key in style.keys():
            if isinstance(style[key], str) and sanitize_hex_color(style[key]):
                style[key] = None
            elif key == "syntax" and isinstance(style[key], dict):
                for syntax_key in style[key]:
                    if "color" in style[key][syntax_key]:
                        style[key][syntax_key]["color"] = None
        self.update_palette_display()

    # Function to save theme and palette
    def save_theme_and_palette(self, folder_name="theme_files"):
        import os
        from tkinter import filedialog

        # Ask user for folder to save files
        save_dir = filedialog.askdirectory(initialdir=".", title="Select Save Directory")
        if not save_dir:
            return

        save_path = os.path.join(save_dir, folder_name)
        os.makedirs(save_path, exist_ok=True)

        # Save palette file
        palette_file = os.path.join(save_path, "palette.txt")
        with open(palette_file, "w") as f:
            unique_colors = set(self.palette)
            for color in unique_colors:
                f.write(rgb_to_hex(color) + "\n")

        # Save theme JSON
        theme_file = os.path.join(save_path, "theme.json")
        with open(theme_file, "w") as f:
            json.dump(self.theme_data, f, indent=4)

        print(f"Theme and palette saved to {save_path}")


def sanitize_hex_color(color_hex):
    """
    Validates and sanitizes a hexadecimal color string.

    Args:
        color_hex (str): The color string to sanitize.

    Returns:
        str: A valid 6-character hexadecimal color string or None if invalid.
    """
    if not isinstance(color_hex, str) or not color_hex.startswith("#"):
        return None

    # Strip leading '#' and handle both 6-digit and 8-digit hex colors
    color_hex = color_hex.lstrip("#")

    if len(color_hex) == 6:  # Standard #RRGGBB
        return f"#{color_hex}"
    elif len(color_hex) == 8:  # #AARRGGBB
        return f"#{color_hex[2:]}"  # Strip alpha channel
    else:
        return None

def add_to_palette(self, color_hex):
    """
    Add a color to the palette, ensuring uniqueness.

    Args:
        color_hex (str): The color to add.
    """
    sanitized_color = sanitize_hex_color(color_hex)
    if sanitized_color and sanitized_color not in self.palette:
        self.palette.append(sanitized_color)
        # Keep the original RGBA for saving purposes if it's 8-digit
        if len(color_hex.lstrip("#")) == 8:
            self.palette_raw.append(color_hex)  # Store the full #AARRGGBB
