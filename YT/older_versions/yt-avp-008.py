#!/usr/bin/env python3
import cv2
import sys
import os
import time
import subprocess
import urllib.parse
import shutil

# Define a brightness gradient from darkest to lightest.
ASCII_CHARS = "@%#*+=-:. "

def pixel_to_ascii(brightness, gamma=0.5):
    """
    Map a brightness value (0-255) to an ASCII character using gamma correction.
    
    Args:
        brightness (int): Pixel brightness (0-255).
        gamma (float): Gamma correction factor; values < 1.0 boost mid-tones.
        
    Returns:
        str: Corresponding ASCII character.
    """
    normalized = brightness / 255.0
    adjusted = normalized ** gamma
    index = int(adjusted * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[index]

def get_terminal_size():
    """Get the terminal window size."""
    columns, rows = shutil.get_terminal_size()
    return columns, rows

def frame_to_ascii_color(frame, gamma=0.5):
    """
    Convert an image frame to colored ASCII art with gamma correction.
    
    Args:
        frame: Image frame (BGR as read by OpenCV).
        gamma: Gamma correction factor for brightness mapping.
    
    Returns:
        A string containing the ASCII art with ANSI color escape sequences.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, _ = frame_rgb.shape
    aspect_ratio = height / width
    term_width, term_height = get_terminal_size()
    new_width = term_width
    new_height = int(aspect_ratio * new_width * 0.55)
    resized_rgb = cv2.resize(frame_rgb, (new_width, new_height))
    gray = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2GRAY)
    
    ascii_art = ''
    for y in range(new_height):
        for x in range(new_width):
            r, g, b = resized_rgb[y, x]
            brightness = gray[y, x]
            char = pixel_to_ascii(brightness, gamma=gamma)
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
        A string containing the URL/path to the video stream.
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
    if len(sys.argv) < 2:
        print("Usage: ./video_to_ascii.py <video_file_or_youtube_url>")
        sys.exit(1)
    
    source = sys.argv[1]
    video_source = get_video_source(source)
    
    cap = cv2.VideoCapture(video_source)
    
    if not cap.isOpened():
        print(f"Error: Unable to open video source '{video_source}'")
        sys.exit(1)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 0.033  
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  
            
            ascii_frame = frame_to_ascii_color(frame, gamma=0.5)
            clear_screen()
            print(ascii_frame)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cap.release()

if __name__ == '__main__':
    main()
