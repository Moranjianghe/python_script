import os
import ffmpeg

def compress_gif_to_10mb(gif_path, max_size_mb=10):
    max_size = max_size_mb * 1024 * 1024
    temp_path = gif_path + ".tmp.gif"
    scale = 1.0
    fps = 15
    min_fps = 5
    min_scale = 0.3
    while os.path.getsize(gif_path) > max_size and (fps > min_fps or scale > min_scale):
        if fps > min_fps:
            fps = max(min_fps, fps - 2)
        elif scale > min_scale:
            scale = max(min_scale, scale - 0.1)
        probe = ffmpeg.probe(gif_path)
        width = int(probe['streams'][0]['width'])
        height = int(probe['streams'][0]['height'])
        new_width = int(width * scale)
        new_height = int(height * scale)
        try:
            (
                ffmpeg
                .input(gif_path)
                .filter('fps', fps=fps)
                .filter('scale', new_width, new_height)
                .output(temp_path)
                .overwrite_output()
                .run(quiet=True)
            )
            os.replace(temp_path, gif_path)
        except ffmpeg.Error as e:
            print(f"壓縮失敗: {gif_path}\n錯誤: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            break
    final_size = os.path.getsize(gif_path)
    if final_size > max_size:
        print(f"無法壓縮到 10MB 以內: {gif_path} (目前大小: {final_size/1024/1024:.2f}MB)")
    else:
        print(f"已壓縮到 10MB 以內: {gif_path} (目前大小: {final_size/1024/1024:.2f}MB)")

if __name__ == "__main__":
    folder = input("請輸入目標資料夾路徑（預設為當前資料夾 .）：").strip() or "."
    for filename in os.listdir(folder):
        if filename.lower().endswith(".gif"):
            gif_path = os.path.join(folder, filename)
            if os.path.getsize(gif_path) > 10 * 1024 * 1024:
                compress_gif_to_10mb(gif_path)
