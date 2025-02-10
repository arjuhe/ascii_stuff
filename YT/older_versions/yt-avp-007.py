#!/usr/bin/env python3
import cv2
import sys
import os
import time
import subprocess
import urllib.parse

# A set of ASCII characters from darkest to lightest.
ASCII_CHARS = "⣿⣷⣶⣴⣤⣄⣀"
"@%#*+=-:."

def pixel_to_ascii(brightness):
    """
    Map a brightness value (0-255) to an ASCII character.
    """
    index = int(brightness / 256 * len(ASCII_CHARS))
    if index >= len(ASCII_CHARS):
        index = len(ASCII_CHARS) - 1
    return ASCII_CHARS[index]

def frame_to_ascii_color(frame, new_width=80):
    """
    Convert an image frame to colored ASCII art.
    
    Args:
        frame: The image frame (BGR, as read by OpenCV).
        new_width: The desired width for the ASCII output.
        
    Returns:
        A string containing the ASCII art with ANSI color escape sequences.
    """
    # Convert the frame from BGR to RGB.
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Get original dimensions and calculate new height to maintain aspect ratio.
    height, width, _ = frame_rgb.shape
    aspect_ratio = height / width
    # 0.55 factor approximates the typical aspect ratio of terminal characters.
    new_height = int(aspect_ratio * new_width * 0.55)
    
    # Resize the RGB frame.
    resized_rgb = cv2.resize(frame_rgb, (new_width, new_height))
    
    # Also compute a grayscale version for brightness mapping.
    gray = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2GRAY)
    
    ascii_art = ''
    for y in range(new_height):
        for x in range(new_width):
            # Get the pixel's color.
            r, g, b = resized_rgb[y, x]
            # Use the grayscale value for determining the ASCII char.
            brightness = gray[y, x]
            char = pixel_to_ascii(brightness)
            # ANSI escape code for setting the foreground color to (r,g,b).
            ascii_art += f'\033[38;2;{r};{g};{b}m{char}\033[0m'
        ascii_art += "\n"
    return ascii_art

def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def get_video_source(source):
    """
    Determine if the provided source is a YouTube URL or a local file.
    For a YouTube URL, use yt-dlp to extract the direct video URL.
    
    Args:
        source (str): YouTube URL or local file path.
    
    Returns:
        A string containing the URL/path to the video stream.
    """
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in ('http', 'https'):
        # Assume it's a YouTube URL and extract the stream URL using yt-dlp.
        try:
            result = subprocess.run(
                ["yt-dlp", "-g", source],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            # yt-dlp may return multiple URLs (e.g., video and audio). Use the first one.
            stream_url = result.stdout.splitlines()[0]
            return stream_url
        except subprocess.CalledProcessError as e:
            print("Error extracting video URL with yt-dlp:")
            print(e.stderr)
            sys.exit(1)
    else:
        # Otherwise, assume it's a local file path.
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
    
    # Retrieve frame rate to control playback speed.
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 0.033  # default ~30 fps if not available
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video stream.
            
            ascii_frame = frame_to_ascii_color(frame)
            clear_screen()
            print(ascii_frame)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        cap.release()

if __name__ == '__main__':
    main()

