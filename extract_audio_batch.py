import os
import ffmpeg

# 運行時輸入目標視頻文件路徑
video_path = input("請輸入視頻文件路徑：").strip()

if not os.path.isfile(video_path):
    print("文件不存在，請檢查路徑。")
    exit(1)

# 支援的視頻文件擴展名
video_extensions = (".mp4", ".webm", ".avi", ".mkv", ".mov", ".flv")

if not video_path.lower().endswith(video_extensions):
    print("不支持的文件格式。支援的格式：.mp4, .webm, .avi, .mkv, .mov, .flv")
    exit(1)

audio_path = os.path.splitext(video_path)[0] + ".aac"

try:
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, vn=None, acodec='copy')
        .run(overwrite_output=True)
    )
    print(f"音頻提取成功：{os.path.basename(audio_path)}")
except ffmpeg.Error as e:
    print(f"音頻提取失敗：{os.path.basename(video_path)}\n錯誤：{e}")
