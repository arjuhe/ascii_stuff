#!/usr/bin/env python3
import cv2
import sys
import os
import time

# A set of ASCII characters from darkest to lightest.
ASCII_CHARS = "@%#*+=-:. "

def frame_to_ascii(frame, new_width=80):
    """
    Convert an image frame to an ASCII representation.
    
    Args:
        frame: The image frame (as a NumPy array).
        new_width: The desired width for the ASCII output.
    
    Returns:
        A string with the ASCII art.
    """
    # Convert the frame to grayscale.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Compute the new height to maintain the aspect ratio.
    height, width = gray.shape
    aspect_ratio = height / width
    # The factor 0.55 roughly compensates for the non-square shape of text characters.
    new_height = int(aspect_ratio * new_width * 0.55)
    
    # Resize the grayscale frame.
    resized_gray = cv2.resize(gray, (new_width, new_height))
    
    # Build the ASCII art string.
    ascii_frame = ""
    for row in resized_gray:
        for pixel in row:
            # Map the pixel value (0-255) to an index for the ASCII_CHARS list.
            index = int(pixel / 256 * len(ASCII_CHARS))
            # Prevent out-of-range indices.
            if index >= len(ASCII_CHARS):
                index = len(ASCII_CHARS) - 1
            ascii_frame += ASCII_CHARS[index]
        ascii_frame += "\n"
    return ascii_frame

def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def main():
    if len(sys.argv) < 2:
        print("Usage: ./video_to_ascii.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    cap = cv2.VideoCapture(video_file)
    
    if not cap.isOpened():
        print(f"Error: Unable to open video file '{video_file}'")
        sys.exit(1)
    
    # Get the video frame rate to time the playback.
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 0.033  # default to ~30 fps if fps info is missing
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # End of video stream.
                break
            
            ascii_frame = frame_to_ascii(frame)
            clear_screen()
            print(ascii_frame)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        # Allow the user to exit early with Ctrl+C.
        print("Exiting...")
    finally:
        cap.release()

if __name__ == '__main__':
    main()
