#!/usr/bin/env python3
import time

CLEAR_SCREEN_CODE = '\033[2J\033[H'  # **DEFINE CLEAR_SCREEN_CODE HERE, BEFORE IT'S USED**

def clear_screen():
    """Clears the terminal screen using ANSI escape codes."""
    print(CLEAR_SCREEN_CODE, end='')

if __name__ == "__main__":
    print("This line should be cleared in 2 seconds...")
    time.sleep(2)
    clear_screen()
    print("Screen should be clear now, only this line should remain.")

