import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
import os

def select_and_extract_audio():
    # Create root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to select MP4 file
    video_path = filedialog.askopenfilename(
        title="Select MP4 Video",
        filetypes=[("MP4 files", "*.mp4")]
    )

    if video_path:
        try:
            # Get the base name without extension
            base_name = os.path.splitext(video_path)[0]
            # Create output WAV filename
            wav_path = base_name + ".wav"
            
            # Load video and extract audio
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(wav_path)
            
            # Close the video and audio to free up resources
            audio.close()
            video.close()
            
            print(f"Audio extracted successfully to: {wav_path}")
            
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
    else:
        print("No file selected")

if __name__ == "__main__":
    select_and_extract_audio()