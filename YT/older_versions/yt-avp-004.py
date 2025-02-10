#!/usr/bin/env python

import sys
import re
import subprocess
import urllib.parse

def extract_video_id(url_or_id):
    """Extract video or playlist ID from a YouTube URL or return it if already an ID."""
    youtube_regex = (r'(?:https?://)?(?:www\.)?'
                     r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)|.*[?&]v=)|'
                     r'youtu\.be/)([^"&?/ ]{11})')
    match = re.search(youtube_regex, url_or_id)
    if match:
        return match.group(1)
    return url_or_id  # Assume it's already a video ID

def extract_playlist_id(url):
    """Extract playlist ID if present in the URL."""
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params.get('list', [None])[0]

def play_video(video_id):
    """Play a single video using mpv."""
    print(f"Playing video: {video_id}")
    subprocess.run(["mpv", f"https://www.youtube.com/watch?v={video_id}"])

def play_playlist(playlist_id):
    """Play a playlist by fetching all video IDs and queuing them in mpv."""
    print(f"Playing playlist: {playlist_id}")
    mpv_process = subprocess.Popen(["mpv", f"https://www.youtube.com/playlist?list={playlist_id}"])
    mpv_process.wait()

def main():
    if len(sys.argv) < 2:
        print("Usage: ./yt-player <YouTube URL or Video ID>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    video_id = extract_video_id(input_arg)
    playlist_id = extract_playlist_id(input_arg)
    
    if playlist_id:
        play_playlist(playlist_id)
    else:
        play_video(video_id)

if __name__ == "__main__":
    main()
