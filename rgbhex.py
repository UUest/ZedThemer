def rgb_to_hex(rgb_color):
    #Converts an RGB tuple to a hex color code.

    return "#{:02x}{:02x}{:02x}".format(*rgb_color)

def hex_to_rgb(hex_color):
    #Converts a hex color code to an RGB tuple.

    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
