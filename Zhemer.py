import json
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
from colorthief import ColorThief
from rgbhex import rgb_to_hex, hex_to_rgb
from PIL import Image, ImageTk

class Zhemer:
    def __init__(self, root):
        self.root = root
        self.root.title("Theme Editor")
        self.root.geometry("800x600")
        self.theme_data = {}
        self.palette = []
        self.palette_raw = []
        self.image_path = ""
        self.image_references = {}

        self.create_widgets()

    def create_widgets(self):
        # Image Section
        self.image_frame = tk.LabelFrame(self.root, text="Image", padx=10, pady=10)
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Palette Section
        self.palette_frame = tk.LabelFrame(self.root, text="Palette", padx=10, pady=10)
        self.palette_frame.pack(fill="x", padx=10, pady=10)

        self.palette_canvas = tk.Canvas(self.palette_frame, height=100)
        self.palette_scrollbar = tk.Scrollbar(self.palette_frame, orient="horizontal", command=self.palette_canvas.xview)
        self.palette_canvas.configure(xscrollcommand=self.palette_scrollbar.set)
        self.add_scrollbar_events_x(self.palette_canvas)

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
        self.add_scrollbar_events_y(self.theme_canvas)

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

        self.clear_theme_button = tk.Button(self.button_frame, text="Clear Theme Colors", command=self.clear_colors)
        self.clear_theme_button.pack(side="left", padx=5)

        self.load_image_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack(side="left", padx=5)

        self.clear_palette_button = tk.Button(self.button_frame, text="Clear Palette", command=self.clear_palette)
        self.clear_palette_button.pack(side="left", padx=5)

        self.load_palette_button = tk.Button(self.button_frame, text="Load Palette", command=self.load_palette)
        self.load_palette_button.pack(side="left", padx=5)

    def sanitize_hex_color(self, color_hex):
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
            flattened_theme = self.flatten_theme(self.theme_data)
            self.theme_data = flattened_theme
            self.extract_palette()
            self.update_theme_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {e}")

    def flatten_theme(self, theme, parent_key=""):
        flattened = {}
        for key, value in theme.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):  # If value is a nested dictionary, recurse
                flattened.update(self.flatten_theme(value, full_key))
            else:
                flattened[full_key] = value
        return flattened

    def nest_theme(self, flattened):
        nested = {}
        for key, value in flattened.items():
            keys = key.split(".")
            d = nested
            for part in keys[:-1]:  # Traverse/create nested dictionaries
                if part not in d:
                    d[part] = {}
                d = d[part]
            d[keys[-1]] = value  # Assign the final value
        return nested

    def load_palette(self):
        palette_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not palette_file:
            return

        try:
            with open(palette_file, "r") as f:
                self.palette = json.load(f)
            self.update_palette_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load palette: {e}")


    def save_theme(self):
        if not self.theme_data:
            messagebox.showerror("Error", "No theme loaded to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not save_path:
            return

        try:
            # Get the base name (without extension) from the save path
            base_name = os.path.splitext(save_path)[0]

            # File paths for theme and palette
            theme_file = save_path  # Main theme file
            palette_file = f"{base_name}_palette.json"  # Palette file

            # Re-nest the theme data
            nested_theme = self.nest_theme(self.theme_data)

            # Save the nested theme JSON
            with open(theme_file, "w") as f:
                json.dump(nested_theme, f, indent=4)

            # Save the palette JSON
            with open(palette_file, "w") as f:
                json.dump(self.palette, f, indent=4)

            messagebox.showinfo("Success", f"Theme saved to {os.path.dirname(save_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme: {e}")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return

        try:
            # Generate color palette from image
            ct = ColorThief(file_path)
            palette = ct.get_palette(color_count=21, quality=1)

            for rgb in palette:
                hex_color = rgb_to_hex(rgb)
                if hex_color not in self.palette:
                    self.palette.append(hex_color)
            self.update_palette_display()

            # Function to display the image after the frame is fully initialized
            def display_image():
                # Open and resize the image
                img = Image.open(file_path)
                img.thumbnail((self.image_frame.winfo_width(), self.image_frame.winfo_height()))  # Fit to frame size

                # Convert to Tkinter-compatible format
                img_tk = ImageTk.PhotoImage(img)

                # Create reference to image to prevent garbage collection
                self.image_references["main_image"] = img_tk

                # Create a label to display the image
                img_label = tk.Label(self.image_frame, image=img_tk, bg="gray")
                img_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the image

            # Use `after` to ensure the frame dimensions are available
            self.image_frame.after(100, display_image)

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

    def clear_palette(self):
        self.palette = []
        self.update_palette_display()

    def update_palette_display(self):
        for widget in self.palette_inner_frame.winfo_children():
            widget.destroy()

        for color in self.palette:
            color_block = tk.Label(self.palette_inner_frame, bg=color, width=4, height=2)
            color_block.pack(side="left", padx=5)

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

            else:
                key_label.config(bg=self.root["bg"])

            change_button = tk.Button(
                color_frame,
                text="New Color",
                command=lambda k=key: self.change_color(k)
            )
            change_button.pack(side="left", padx=5)

            palette_button = tk.Button(
                color_frame,
                text="From Palette",
                command=lambda key=key: self.open_palette_window(
                        set_color_callback=lambda c: self.change_color(key, c)
                )
            )
            palette_button.pack(side="left", padx=5)
            row += 1

    def change_color(self, key, color=None):
        if not color:  # If no color is passed, open the color chooser
            color = colorchooser.askcolor()[1]
        if not color:
            return  # Exit if no color is selected

        self.update_theme_color(key, color)
        self.update_palette_display()

    def open_palette_window(self, set_color_callback):
        palette_window = tk.Toplevel(self.root)  # Use self.root as the parent
        palette_window.title("Palette")
        palette_window.geometry("400x300")

        # Create a scrollable frame for palette colors
        canvas = tk.Canvas(palette_window)
        scrollbar = tk.Scrollbar(palette_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.add_scrollbar_events_y(canvas)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add buttons for each color in the palette
        for color in self.palette:
            button = tk.Button(
                scrollable_frame,
                text=color,
                bg=color,
                command=lambda c=color: [set_color_callback(c), palette_window.destroy()]
            )
            button.pack(pady=5, padx=5, fill="x")
    def select_color_from_palette(self, palette_window, set_color_callback, color):
        set_color_callback(color)
        palette_window.destroy()


    def update_theme_color(self, key, new_color):
        sanitized_color = self.sanitize_hex_color(new_color)
        if not sanitized_color:
            print(f"Invalid color: {new_color}")
            return

        style = self.theme_data.get("themes", [{}])[0].get("style", {})
        if key in style:
            style[key] = sanitized_color

        self.update_theme_display()
        if new_color not in self.palette:
            self.palette.append(new_color)

    def add_scrollbar_events_y(self, canvas):
        # Bind mouse wheel events
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # For Windows/macOS

        def _on_linux_scroll(event):
            if event.num == 4:  # Scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                canvas.yview_scroll(1, "units")

        # Platform-specific event binding
        if self.root.tk.call("tk", "windowingsystem") == "x11":  # Linux (X11)
            canvas.bind("<Button-4>", _on_linux_scroll)
            canvas.bind("<Button-5>", _on_linux_scroll)
        else:  # Windows and macOS
            canvas.bind("<MouseWheel>", _on_mousewheel)


    def add_scrollbar_events_x(self, canvas):
        # Bind mouse wheel events
        def _on_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")  # For Windows/macOS

        def _on_linux_scroll(event):
            if event.num == 4:  # Scroll up
                canvas.xview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                canvas.xview_scroll(1, "units")

        # Platform-specific event binding
        if self.root.tk.call("tk", "windowingsystem") == "x11":  # Linux (X11)
            canvas.bind("<Button-4>", _on_linux_scroll)
            canvas.bind("<Button-5>", _on_linux_scroll)
        else:  # Windows and macOS
            canvas.bind("<MouseWheel>", _on_mousewheel)
