import sys
import re
import subprocess
import urllib.parse

def extract_id(url_or_id):
    """Determine if the input is a video ID or URL and extract the ID."""
    youtube_video_regex = r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})"
    youtube_playlist_regex = r"list=([\w-]+)"
    
    if re.match(r"^[\w-]{11}$", url_or_id):
        return url_or_id, "video"
    elif "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        video_match = re.search(youtube_video_regex, url_or_id)
        playlist_match = re.search(youtube_playlist_regex, url_or_id)
        
        if playlist_match:
            return playlist_match.group(1), "playlist"
        elif video_match:
            return video_match.group(1), "video"
    
    print("Invalid YouTube ID or URL.")
    sys.exit(1)

def play_video(video_id):
    """Play a single YouTube video using mpv."""
    command = ["mpv", f"https://www.youtube.com/watch?v={video_id}"]
    print(f"Playing video: {video_id}")
    print(f"Executing: {' '.join(command)}")
    subprocess.run(command)

def play_playlist(playlist_id):
    """Play a YouTube playlist using mpv."""
    command = ["mpv", f"https://www.youtube.com/playlist?list={playlist_id}"]
    print(f"Playing playlist: {playlist_id}")
    print(f"Executing: {' '.join(command)}")
    subprocess.run(command)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./yt-player <YouTube Video ID or URL>")
        sys.exit(1)
    
    input_value = sys.argv[1]
    video_or_playlist_id, media_type = extract_id(input_value)
    
    print(f"Detected {media_type}: {video_or_playlist_id}")
    
    if media_type == "video":
        play_video(video_or_playlist_id)
    elif media_type == "playlist":
        play_playlist(video_or_playlist_id)

if __name__ == "__main__":
    main()
