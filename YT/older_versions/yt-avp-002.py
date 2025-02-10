import sys
import re
import subprocess
import yt_dlp
from urllib.parse import urlparse, parse_qs

def extract_video_id(url_or_id):
    """Determine if input is a URL or ID, and extract the video or playlist ID."""
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):  # YouTube video IDs are 11 chars long
        return url_or_id, 'video'
    
    parsed_url = urlparse(url_or_id)
    query_params = parse_qs(parsed_url.query)
    
    if 'list' in query_params:
        return query_params['list'][0], 'playlist'
    elif 'v' in query_params:
        return query_params['v'][0], 'video'
    else:
        print("Invalid YouTube URL or ID.")
        sys.exit(1)

def get_playlist_videos(playlist_id):
    """Retrieve video URLs from a YouTube playlist using yt_dlp."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlist_items': '1-',  # Get all items
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/playlist?list={playlist_id}', download=False)
        if 'entries' in info:
            return [entry['url'] for entry in info['entries']]
        else:
            print("Failed to retrieve playlist.")
            sys.exit(1)

def play_video(video_id):
    """Play a single YouTube video using mpv."""
    subprocess.run(["mpv", f"https://www.youtube.com/watch?v={video_id}"])

def play_playlist(playlist_videos):
    """Play a playlist by iterating through video URLs in order."""
    for video_url in playlist_videos:
        subprocess.run(["mpv", video_url])

def main():
    if len(sys.argv) < 2:
        print("Usage: ./yt-player <YouTube Video ID or URL>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    content_id, content_type = extract_video_id(input_arg)
    
    if content_type == 'video':
        play_video(content_id)
    elif content_type == 'playlist':
        videos = get_playlist_videos(content_id)
        play_playlist(videos)

if __name__ == "__main__":
    main()
