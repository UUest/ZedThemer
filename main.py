from email.policy import default
import argparse
import random
import sys
import os
from colorthief import ColorThief
from prompt_toolkit import prompt
from colors import complementary_color, print_color_block
from rgbhex import hex_to_rgb, rgb_to_hex
from theme import load_theme_json, save_theme_json
import colors

def main():
    parser = argparse.ArgumentParser(description="Generate and edit Zed theme color palletes.")
    parser.add_argument("--image", "-i", help="Path to the image file")
    parser.add_argument("--colors", "-c", type=int, default=10, help="Number of colors in the palette")
    parser.add_argument("--quality", "-q", type=int, default=1, help="ColorThief quality parameter (1 = best, higher = faster)")
    parser.add_argument("--theme", "-t", default="theme.json", help="Path to theme configuration JSON file")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print("Image file does not exist.")
        sys.exit(1)

    # ColorThief on image to get palette
    ct = ColorThief(args.image)
    palette = ct.get_palette(color_count=args.colors, quality=args.quality)

    # Load existing theme if specified
    theme_data = load_theme_json(args.theme)

    # Main Loop
    while True:
        print("\nCurrent Palette:")
        for i, color in enumerate(palette):
            label = ""
            # Check if color is assigned in theme_data
            for k, v in theme_data.items():
                if v.lower() == rgb_to_hex(color).lower():
                    label = f" (assigned to {k})"
                    break
            print_color_block(color, label=label)

        print("\nMenu:")
        print("1) Add color")
        print("2) Remove color")
        print("3) Edit color")
        print("4) Assign color to theme key")
        print("5) Show complementary color suggestion")
        print("6) Save & Exit")
        print("7) Exit without saving")

        choice = prompt("Choose an option: ").strip()

        match choice:
            case '1':
                print("Add color options:")
                print("a) From hex input")
                print("b) Random complementary to an existing color")
                print("c) Random RGB")
                method = prompt("Choose add method: ").strip()

                match method:
                    case 'a':
                        user_hex = prompt("Enter hex color (e.g., #AABBCC): ").strip()
                        try:
                            new_color = hex_to_rgb(user_hex)
                            palette.append(new_color)
                        except ValueError:
                            print("Invalid hex code.")
                    case 'b':
                        if not palette:
                            print("No colors to base complementary color on.")
                        else:
                            idx = prompt(f"Enter index of base color (0-{len(palette)-1}): ").strip()
                            if idx.isdigit():
                                idx = int(idx)
                                if 0 <= idx < len(palette):
                                    new_color = complementary_color(palette[idx])
                                    palette.append(new_color)
                                else:
                                    print("Invalid index.")
                    case 'c':
                        # Randomize RGB values
                        new_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0,255))
                        palette.append(new_color)
                    case '':
                        print("Invalid choice.")
            case '2':
                # Remove color
                idx = prompt(f"Enter index of color to remove (0-{len(palette)-1}): ").strip()
                if idx.isdigit():
                    idx = int(idx)
                    if 0 <= idx < len(palette):
                        del palette[idx]
                    else:
                        print("Index out of range.")
            case '3':
                # Edit color
                idx = prompt(f"Enter index of color to edit (0-{len(palette)-1}): ").strip()
                if idx.isdigit():
                    idx = int(idx)
                    if 0 <= idx < len(palette):
                        old_color = palette[idx]
                        print_color_block(old_color, label="Current")
                        new_hex = prompt("Enter new hex color: ").strip()
                        try:
                            new_color = hex_to_rgb(new_hex)
                            palette[idx] = new_color
                        except ValueError:
                            print("Invalid hex code.")
                    else:
                        print("Index out of range.")
            case '4':
                # Assign color to theme key
                idx = prompt(f"Enter index of color to assign (0-{len(palette)-1}): ").strip()
                if idx.isdigit():
                    idx = int(idx)
                    if 0 <= idx < len(palette):
                        key = prompt("Enter the theme key to assign this color to: ").strip()
                        hex_val = rgb_to_hex(palette[idx])
                        theme_data[key] = hex_val
                        print(f"Assigned {hex_val} to {key}.")
                    else:
                        print("Index out of range.")
            case '5':
                # Suggest complementary colors for each palette color
                print("Complementary suggestions:")
                for i, c in enumerate(palette):
                    comp = complementary_color(c)
                    print(f"Color {i}:")
                    print_color_block(c, "Original")
                    print_color_block(comp, "Complementary suggestion")
            case '6':
                # Save & exit
                save_theme_json(args.theme, theme_data)
                print("Changes Saved. Exiting.")
                break
            case '7':
                # Exit, no save
                print("Exiting without saving.")
                break
            case '':
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
