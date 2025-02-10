#!/usr/bin/env python3
"""
yt-avp{version}.py
Version: {version}
Codename: liquid
Beta ASCII Video Player
""".format(version=".012")

import cv2
import sys
import os
import time
import subprocess
import urllib.parse
import shutil
import argparse

# Versioning and codename
VERSION = ".012"
CODENAME = "liquid"

# Default ASCII gradient from darkest to lightest (16 characters, no blank)
DEFAULT_ASCII_GRADIENT = "@%#*+=-:./\\|~<>?"

# Braille gradient from darkest to lightest (16 characters, no blank)
BRAILLE_ASCII_GRADIENT = "⣿⣷⣯⣟⡿⢿⣻⣽⣾⡾⣷⣯⣟⡿⢿⣻⣽"

def pixel_to_ascii(brightness, gamma=0.5, gradient=DEFAULT_ASCII_GRADIENT):
    """
    Map a brightness value (0-255) to an ASCII character using gamma correction.
    
    Args:
        brightness (int): Pixel brightness (0-255).
        gamma (float): Gamma correction factor; values < 1.0 boost mid-tones.
        gradient (str): A string of ASCII characters ordered from darkest to lightest.
        
    Returns:
        str: Corresponding ASCII character.
    """
    normalized = brightness / 255.0
    adjusted = normalized ** gamma
    index = int(adjusted * (len(gradient) - 1))
    return gradient[index]

def get_terminal_size():
    """Get the terminal window size."""
    columns, rows = shutil.get_terminal_size()
    return columns, rows

def frame_to_ascii_color(frame, gamma=0.5, gradient=DEFAULT_ASCII_GRADIENT, max_width=None, max_height=None):
    """
    Convert an image frame to colored ASCII art with gamma correction.
    
    Args:
        frame: Image frame (BGR as read by OpenCV).
        gamma (float): Gamma correction factor.
        gradient (str): A string of ASCII characters for brightness mapping.
        max_width (int): Maximum width for the ASCII output (optional).
        max_height (int): Maximum height for the ASCII output (optional).
    
    Returns:
        str: The ASCII art with ANSI color escape sequences.
    """
    # Convert frame from BGR to RGB.
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, _ = frame_rgb.shape
    aspect_ratio = height / width

    # Get terminal dimensions.
    term_width, term_height = get_terminal_size()
    # Determine new width based on terminal width and optional max_width.
    new_width = min(term_width, max_width) if max_width else term_width
    # Calculate new height from aspect ratio and scale factor (0.55 approximates terminal character aspect ratio).
    new_height = int(aspect_ratio * new_width * 0.55)
    if max_height:
        new_height = min(new_height, max_height)
    
    resized_rgb = cv2.resize(frame_rgb, (new_width, new_height))
    gray = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2GRAY)
    
    ascii_art = ''
    for y in range(new_height):
        for x in range(new_width):
            r, g, b = resized_rgb[y, x]
            brightness = gray[y, x]
            char = pixel_to_ascii(brightness, gamma=gamma, gradient=gradient)
            # Use ANSI escape codes for 24-bit color.
            ascii_art += f'\033[38;2;{r};{g};{b}m{char}\033[0m'
        ascii_art += "\n"
    return ascii_art

def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def get_video_source(source):
    """
    Determine if the provided source is a YouTube URL or a local file.
    If it's a YouTube URL, use yt-dlp to extract the direct video stream URL.
    
    Args:
        source (str): YouTube URL or local file path.
    
    Returns:
        str: The URL/path to the video stream.
    """
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in ('http', 'https'):
        try:
            result = subprocess.run(
                ["yt-dlp", "-g", source],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            stream_url = result.stdout.splitlines()[0]
            return stream_url
        except subprocess.CalledProcessError as e:
            print("Error extracting video URL with yt-dlp:")
            print(e.stderr)
            sys.exit(1)
    else:
        return source

def main():
    parser = argparse.ArgumentParser(
        description="Video to ASCII Converter: Render videos as colored ASCII art in your terminal."
    )
    parser.add_argument("source", help="Video file path or YouTube URL.")
    parser.add_argument("-g", "--gradient", choices=["default", "braille"], default="default",
                        help="Select the ASCII gradient to use. 'default' uses standard ASCII characters, 'braille' uses a braille character gradient.")
    parser.add_argument("-G", "--gamma", type=float, default=0.5,
                        help="Gamma correction factor (default: 0.5).")
    parser.add_argument("--max-width", type=int, default=None,
                        help="Maximum width for the ASCII output (optional).")
    parser.add_argument("--max-height", type=int, default=None,
                        help="Maximum height for the ASCII output (optional).")
    
    args = parser.parse_args()
    
    # Choose gradient based on parameter.
    if args.gradient == "braille":
        gradient = BRAILLE_ASCII_GRADIENT
    else:
        gradient = DEFAULT_ASCII_GRADIENT

    video_source = get_video_source(args.source)
    
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"Error: Unable to open video source '{video_source}'")
        sys.exit(1)
    
    # Default playback dimensions are based on video dimensions.
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 0.033
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ascii_frame = frame_to_ascii_color(frame, gamma=args.gamma, gradient=gradient,
                                               max_width=args.max_width, max_height=args.max_height)
            clear_screen()
            print(ascii_frame)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cap.release()

if __name__ == '__main__':
    main()
