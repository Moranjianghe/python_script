import os
import subprocess
from pathlib import Path

def convert_heic_to_png_with_imagemagick(heic_path: Path, output_path: Path) -> bool:
    """
    使用 ImageMagick 轉換 HEIC 到 PNG。
    需要先安裝 ImageMagick，並確保 magick 命令可用。
    """
    try:
        result = subprocess.run(
            ["magick", str(heic_path), str(output_path)],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"ImageMagick 轉換失敗: {e}")
        return False
    except FileNotFoundError:
        print("未找到 ImageMagick 的 magick 命令。請先安裝 ImageMagick。")
        return False

# 範例使用
heic_file = Path(r"F:\download\新增資料夾 (6)\IMG_9240.HEIC")
png_file = heic_file.with_suffix('.png')

if convert_heic_to_png_with_imagemagick(heic_file, png_file):
    print(f"成功轉換: {heic_file} -> {png_file}")
else:
    print("轉換失敗")