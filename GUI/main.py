from logging import exception
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
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
        # Clear previous content
        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        if not self.palette and not self.theme_data:
            empty_label = tk.Label(self.palette_frame, text="No palette or theme loaded.", font=("Arial", 12))
            empty_label.pack()
            return

        # Display colors in the palette
        if self.palette:
            tk.Label(self.palette_frame, text="Image Palette:", font=("Arial", 12, "bold")).pack(anchor="w")
            for color in self.palette:
                color_hex = rgb_to_hex(color)
                color_block = tk.Label(self.palette_frame, text=color_hex, bg=color_hex, fg="white", width=20, height=2)
                color_block.pack(pady=2, padx=5)

        # Display theme data colors
        if self.theme_data:
            tk.Label(self.palette_frame, text="Theme Colors:", font=("Arial", 12, "bold")).pack(anchor="w")
            style = self.theme_data.get("themes", [{}])[0].get("style", {})
            for key, value in style.items():
                if isinstance(value, str) and value.startswith("#"):
                    color_block = tk.Label(self.palette_frame, text=f"{key}: {value}", bg=value, fg="white", width=30, height=2)
                    color_block.pack(pady=2, padx=5)


def main():
    root = tk.Tk()  # Create the main application window
    app = Zhemer(root)  # Instantiate the app class
    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()
