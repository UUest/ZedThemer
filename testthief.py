from colorthief import ColorThief
from rgbhex import rgb_to_hex

color_thief = ColorThief(file='./rain_group.png')

dominant_color = color_thief.get_color(quality=1)

color_pallet = color_thief.get_palette(color_count=10, quality=1)

# Generate Hex pallete fro RGB pallete
hex_pallete = []
hex_color = rgb_to_hex(dominant_color)

for color in color_pallet:
    hex_pallete.append(rgb_to_hex(color))

print(hex_pallete)
print(hex_color)
