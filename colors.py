from rgbhex import rgb_to_hex
# ANSI escape sequences for 24-bit color
# For background color: \x1b[48;2;R;G;Bm
# For foreground color: \x1b[38;2;R;G;Bm
RESET = "\x1b[0m"


def print_color_block(rgb, label=""):
    R, G, B = rgb
    block = f"\x1b[48;2;{R};{G};{B}m  {RESET}"
    # Display a block and the hex value
    print(f"{block} {rgb_to_hex(rgb)} {label}")

def complementary_color(rgb):
    # invert RGB to find complementary color
    R, G, B = rgb
    return (255 - R, 255 - G, 255 - B)
