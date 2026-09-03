import sys
import os
import yt_dlp

# Define your permanent download folder here
DOWNLOAD_FOLDER = r"D:\downloaded youtube videos"

def main():
    if len(sys.argv) < 2:
        print("Error: Missing YouTube URL.")
        print("Usage: python download_audio.py <YOUTUBE_URL>")
        sys.exit(1)

    video_url = sys.argv[1]

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    
    mp3_path = download(video_url)
    print(mp3_path)


def download(video_url):
        ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False fetches data without downloading the file yet
            info_dict = ydl.extract_info(video_url, download=True)
            
            # This gives the path yt-dlp expects to make (e.g., "path/title.webm")
            expected_path = ydl.prepare_filename(info_dict)
            
            # Change the extension to .mp3 since the postprocessor converts it
            mp3_path = os.path.splitext(expected_path)[0] + '.mp3'
            file_name = os.path.basename(mp3_path)
        return mp3_path








if __name__ == "__main__":
    main()