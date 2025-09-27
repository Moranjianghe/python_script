import os
import ffmpeg

# 運行時輸入目標資料夾路徑，預設為當前資料夾
folder = input("請輸入目標資料夾路徑（預設為當前資料夾 .）：").strip() or "."

# 支援的視頻文件擴展名
video_extensions = (".mp4", ".webm", ".avi", ".mkv", ".mov", ".flv")

for filename in os.listdir(folder):
    if filename.lower().endswith(video_extensions):
        video_path = os.path.join(folder, filename)
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        try:
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, vn=None, acodec='libmp3lame', ab='192k')
                .run(overwrite_output=True)
            )
            print(f"Extracted audio: {filename} -> {os.path.basename(audio_path)}")
        except ffmpeg.Error as e:
            print(f"Failed to extract audio: {filename}\nError: {e}")
