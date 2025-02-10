#!/usr/bin/env python3

import sys
import re
import subprocess
import yt_dlp

def is_youtube_url(input_str):
    youtube_video_pattern = re.compile(r"(?:v=|youtu\.be/|embed/|shorts/|/v/|/e/|/watch\?v=|/videos/|/video/|/watch\?feature=player_embedded&v=)([A-Za-z0-9_-]{11})")
    youtube_playlist_pattern = re.compile(r"(?:list=)([A-Za-z0-9_-]+)")
    
    video_match = youtube_video_pattern.search(input_str)
    playlist_match = youtube_playlist_pattern.search(input_str)
    
    video_id = video_match.group(1) if video_match else None
    playlist_id = playlist_match.group(1) if playlist_match else None
    
    return video_id, playlist_id

def play_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    print("Playing: " + url)
    subprocess.run(["mpv", url])

def play_playlist(playlist_id):
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    ydl_opts = {'quiet': True, 'extract_flat': True, 'playlistend': 100}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if 'entries' in info:
            video_urls = [entry['url'] for entry in info['entries'] if 'url' in entry]
            for video in video_urls:
                print("Playing: " + video)
                subprocess.run(["mpv", video])

if __name__ == "__main__":
    input_data = sys.stdin.read().strip()
    video_id, playlist_id = is_youtube_url(input_data)
    
    if playlist_id:
        print("Found Playlist ID: " + playlist_id)
        play_playlist(playlist_id)
    elif video_id:
        print("Found Video ID: " + video_id)
        play_video(video_id)
    else:
        print("No Valid YouTube ID or URL Found.")
