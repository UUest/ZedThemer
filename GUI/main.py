import json
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
from colorthief import ColorThief

class ThemeEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Theme Editor")
        self.root.geometry("800x600")
        self.theme_data = {}
        self.palette = []
        self.palette_raw = []
        self.image_path = ""

        self.create_widgets()

    def create_widgets(self):
        # Image Section
        self.image_frame = tk.LabelFrame(self.root, text="Image", padx=10, pady=10)
        self.image_frame.pack(fill="x", padx=10, pady=10)

        # Palette Section
        self.palette_frame = tk.LabelFrame(self.root, text="Palette", padx=10, pady=10)
        self.palette_frame.pack(fill="x", padx=10, pady=10)

        self.palette_canvas = tk.Canvas(self.palette_frame, height=100)
        self.palette_scrollbar = tk.Scrollbar(self.palette_frame, orient="horizontal", command=self.palette_canvas.xview)
        self.palette_canvas.configure(xscrollcommand=self.palette_scrollbar.set)

        self.palette_inner_frame = tk.Frame(self.palette_canvas)
        self.palette_inner_frame.bind("<Configure>", lambda e: self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all")))
        self.palette_canvas.create_window((0, 0), window=self.palette_inner_frame, anchor="nw")

        self.palette_canvas.pack(side="top", fill="x", expand=True)
        self.palette_scrollbar.pack(side="bottom", fill="x")

        # Theme Display Section
        self.theme_frame = tk.LabelFrame(self.root, text="Theme", padx=10, pady=10)
        self.theme_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.theme_canvas = tk.Canvas(self.theme_frame)
        self.theme_scrollbar = tk.Scrollbar(self.theme_frame, orient="vertical", command=self.theme_canvas.yview)
        self.theme_canvas.configure(yscrollcommand=self.theme_scrollbar.set)

        self.theme_inner_frame = tk.Frame(self.theme_canvas)
        self.theme_inner_frame.bind("<Configure>", lambda e: self.theme_canvas.configure(scrollregion=self.theme_canvas.bbox("all")))
        self.theme_canvas.create_window((0, 0), window=self.theme_inner_frame, anchor="nw")

        self.theme_canvas.pack(side="left", fill="both", expand=True)
        self.theme_scrollbar.pack(side="right", fill="y")

        # Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill="x", padx=10, pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Theme", command=self.load_theme)
        self.load_button.pack(side="left", padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Theme", command=self.save_theme)
        self.save_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Colors", command=self.clear_colors)
        self.clear_button.pack(side="left", padx=5)

    def sanitize_hex_color(self, color_hex):
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

    def load_theme(self):
        theme_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not theme_file:
            return

        try:
            with open(theme_file, "r") as f:
                self.theme_data = json.load(f)
            self.extract_palette()
            self.update_theme_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {e}")

    def save_theme(self):
        if not self.theme_data:
            messagebox.showerror("Error", "No theme loaded to save.")
            return

        save_folder = filedialog.askdirectory()
        if not save_folder:
            return

        try:
            theme_name = self.theme_data.get("name", "theme").replace(" ", "_")
            theme_file = os.path.join(save_folder, f"{theme_name}.json")
            palette_file = os.path.join(save_folder, f"{theme_name}_palette.json")

            with open(theme_file, "w") as f:
                json.dump(self.theme_data, f, indent=4)

            with open(palette_file, "w") as f:
                json.dump(self.palette, f, indent=4)

            messagebox.showinfo("Success", f"Theme saved to {save_folder}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme: {e}")

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

    def clear_colors(self):
        if not self.theme_data:
            return

        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        for key in style.keys():
            if isinstance(style[key], str) and style[key].startswith("#"):
                style[key] = None

        if "syntax" in style and isinstance(style["syntax"], dict):
            for syntax_key, syntax_val in style["syntax"].items():
                if isinstance(syntax_val, dict) and "color" in syntax_val:
                    syntax_val["color"] = None

        self.update_theme_display()

    def extract_palette(self):
        self.palette = []
        style = self.theme_data.get("themes", [{}])[0].get("style", {})

        for key, color in style.items():
            if isinstance(color, str) and color.startswith("#"):
                sanitized = self.sanitize_hex_color(color)
                if sanitized and sanitized not in self.palette:
                    self.palette.append(sanitized)

        if "syntax" in style and isinstance(style["syntax"], dict):
            for syntax_val in style["syntax"].values():
                if isinstance(syntax_val, dict) and "color" in syntax_val:
                    color = syntax_val["color"]
                    sanitized = self.sanitize_hex_color(color)
                    if sanitized and sanitized not in self.palette:
                        self.palette.append(sanitized)

        self.update_palette_display()

    def update_palette_display(self):
        for widget in self.palette_inner_frame.winfo_children():
            widget.destroy()

        for color in self.palette:
            color_block = tk.Label(self.palette_inner_frame, bg=color, width=4, height=2)
            color_block.pack(side="left", padx=2)

    def update_theme_display(self):
        for widget in self.theme_inner_frame.winfo_children():
            widget.destroy()

        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        row = 0

        for key, value in style.items():
            color_frame = tk.Frame(self.theme_inner_frame)
            color_frame.grid(row=row, column=0, sticky="w", padx=5, pady=2)

            key_label = tk.Label(color_frame, text=key, width=30, anchor="w")
            key_label.pack(side="left")

            if isinstance(value, str) and value.startswith("#"):
                color = self.sanitize_hex_color(value)
                if color:
                    color_block = tk.Label(color_frame, bg=color, width=4, height=2)
                    color_block.pack(side="left", padx=5)

                    change_button = tk.Button(color_frame, text="Change", command=lambda k=key: self.change_color(k))
                    change_button.pack(side="left", padx=5)
            else:
                key_label.config(bg=self.root["bg"])

            row += 1

    def change_color(self, key):
        color = colorchooser.askcolor()[1]
        if not color:
            return

        self.update_theme_color(key, color)

    def update_theme_color(self, key, new_color):
        sanitized_color = self.sanitize_hex_color(new_color)
        if not sanitized_color:
            print(f"Invalid color: {new_color}")
            return

        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        if key in style:
            style[key] = sanitized_color

        self.update_theme_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = ThemeEditorApp(root)
    root.mainloop()
