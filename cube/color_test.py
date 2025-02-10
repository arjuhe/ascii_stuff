# color_test.py
import os

# ANSI color codes
COLOR_RESET = '\033[0m'
COLOR_BRIGHT_GREEN = '\033[92m'
COLOR_NORMAL = '\033[0m' # Normal/Reset color

def test_colors():
    """Prints lines of text with different ANSI color codes."""

    print("Color Test Script:\n")

    # Bright Green Text
    bright_green_line = f"{COLOR_BRIGHT_GREEN}This text should be bright green.{COLOR_RESET}"
    print(bright_green_line)

    # Normal Color Text (using COLOR_RESET, though it might be default already)
    normal_color_line = f"{COLOR_NORMAL}and this should be normal color.{COLOR_RESET}" # Explicitly using COLOR_NORMAL
    print(normal_color_line)

    print("\nTesting other basic colors:\n")

    colors_to_test = {
        "Bright Red": '\033[91m',
        "Neutral Green": '\033[92m',
        "Bright Blue": '\033[94m',
        "Bright Yellow (Outline)": '\033[93m',
        "Red": '\033[31m',
        "Green": '\033[32m',
        "Blue": '\033[34m',
        "Yellow": '\033[33m',
        "Cyan": '\033[36m',
        "Magenta": '\033[35m',
        "White": '\033[37m',
        "Black": '\033[30m',
        "Bright Black": '\033[90m',
        "Bright White": '\033[97m',
        "Bright Cyan": '\033[96m',
        "Bright Magenta": '\033[95m'
    }

    for color_name, color_code in colors_to_test.items():
        test_line = f"{color_code}This is {color_name} text.{COLOR_RESET}"
        print(test_line)


if __name__ == "__main__":
    test_colors()