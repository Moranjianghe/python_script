import os
import ffmpeg

# 運行時輸入目標資料夾路徑，預設為當前資料夾
folder = input("請輸入目標資料夾路徑（預設為當前資料夾 .）：").strip() or "."

for filename in os.listdir(folder):
    if filename.lower().endswith(".mp4"):
        mp4_path = os.path.join(folder, filename)
        gif_path = os.path.splitext(mp4_path)[0] + ".gif"
        try:
            (
                ffmpeg
                .input(mp4_path)
                .output(gif_path)
                .run(overwrite_output=True)
            )
            os.remove(mp4_path)
            print(f"Converted and removed: {filename}")
        except ffmpeg.Error as e:
            print(f"Failed to convert: {filename}\nError: {e}")