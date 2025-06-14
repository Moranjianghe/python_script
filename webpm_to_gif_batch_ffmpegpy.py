import os
import ffmpeg

# 運行時輸入目標資料夾路徑，預設為當前資料夾
folder = input("請輸入目標資料夾路徑（預設為當前資料夾 .）：").strip() or "."

for filename in os.listdir(folder):
    if filename.lower().endswith(".webm"):
        webm_path = os.path.join(folder, filename)
        gif_path = os.path.splitext(webm_path)[0] + ".gif"
        try:
            (
                ffmpeg
                .input(webm_path)
                .output(gif_path)
                .run(overwrite_output=True)
            )
            os.remove(webm_path)
            print(f"Converted and removed: {filename}")
        except ffmpeg.Error as e:
            print(f"Failed to convert: {filename}\nError: {e}")