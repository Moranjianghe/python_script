import os
from pathlib import Path
from typing import Iterable
from PIL import Image  # 需要先安裝: pip install pillow

# 可選套件 (若安裝, 匯入會註冊對應的 Image plugin):
# - pillow-avif-plugin (pypi name: pillow-avif-plugin)
# - pillow-jxl-plugin  (pypi name: pillow-jxl-plugin)
try:
    import pillow_avif  # type: ignore
except Exception:
    HAS_AVIF = False
else:
    HAS_AVIF = True

try:
    import pillow_jxl  # type: ignore
except Exception:
    HAS_JXL = False
else:
    HAS_JXL = True

try:
    import pillow_heif  # type: ignore
except Exception:
    HAS_HEIC = False
else:
    HAS_HEIC = True

SUPPORTED_INPUT_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".avif",
    ".jxl",
    ".heic",
    ".heif",
}
FORMAT_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "bmp": "BMP",
    "tiff": "TIFF",
    "tif": "TIFF",
    "webp": "WEBP",
    "avif": "AVIF",
    "jxl": "JXL",
    "heic": "HEIC",
    "heif": "HEIF",
}


def collect_images(paths: Iterable[Path]) -> list[Path]:
    images = []
    for item in paths:
        if item.is_file() and item.suffix.lower() in SUPPORTED_INPUT_EXTS:
            images.append(item)
    return images


def normalize_target_format(fmt: str) -> str:
    fmt = fmt.strip().lower()
    if fmt not in FORMAT_MAP:
        raise ValueError(f"不支援的目標格式: {fmt}")
    return fmt


def prompt_yes_no(message: str, default: bool = False) -> bool:
    choice = input(message).strip().lower()
    if not choice:
        return default
    return choice in {"y", "yes"}


def prompt_int(message: str, default: int, minimum: int, maximum: int) -> int:
    while True:
        raw = input(message).strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("❌ 輸入必須為整數，請再試一次")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"❌ 範圍應為 {minimum}-{maximum}，請再試一次")


def get_default_save_kwargs(target_format: str) -> dict[str, object]:
    save_format = FORMAT_MAP[target_format]
    if save_format == "JPEG":
        return {"quality": 90}
    return {}


def prompt_save_options(target_format: str) -> dict[str, object]:
    options: dict[str, object] = {}
    fmt = target_format
    if fmt in {"jpg", "jpeg"}:
        quality = prompt_int("請輸入 JPEG 畫質 (1-100，預設90): ", 90, 1, 100)
        options["quality"] = quality
    elif fmt == "webp":
        if prompt_yes_no("是否使用無損 WebP？[y/N]: "):
            options["lossless"] = True
        else:
            quality = prompt_int("請輸入 WebP 畫質 (0-100，預設80): ", 80, 0, 100)
            options["quality"] = quality
    elif fmt == "avif":
        if prompt_yes_no("是否使用 AVIF 無損模式？[y/N]: "):
            options["quality_mode"] = "lossless"
        else:
            quality = prompt_int("請輸入 AVIF 畫質 (0-100，預設80): ", 80, 0, 100)
            options["quality"] = quality
    elif fmt == "jxl":
        if prompt_yes_no("是否使用 JPEG XL 無損模式？[y/N]: "):
            options["lossless"] = True
        else:
            quality = prompt_int("請輸入 JPEG XL 畫質 (0-100，預設75): ", 75, 0, 100)
            options["quality"] = quality
    elif fmt in {"heic", "heif"}:
        if prompt_yes_no("是否使用 HEIC/HEIF 無損模式？[y/N]: "):
            options["lossless"] = True
        else:
            quality = prompt_int("請輸入 HEIC/HEIF 畫質 (0-100，預設80): ", 80, 0, 100)
            options["quality"] = quality
    elif fmt == "png":
        compress_level = prompt_int("請輸入 PNG 壓縮等級 (0-9，預設6): ", 6, 0, 9)
        options["compress_level"] = compress_level
    return options


def convert_image(
    source: Path,
    target_format: str,
    output_dir: Path | None,
    overwrite: bool,
    save_options: dict[str, object] | None = None,
) -> bool:
    output_dir = output_dir or source.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    target_name = f"{source.stem}.{target_format}"
    target_path = output_dir / target_name

    if target_path.exists() and not overwrite:
        print(f"⚠️ 已存在，跳過: {target_path}")
        return False

    save_format = FORMAT_MAP[target_format]

    if source.suffix.lower() in {".heic", ".heif"} and not HAS_HEIC:
        print("❌ 轉換失敗: 需要安裝 pillow-heif 才能讀取 HEIC/HEIF 格式")
        return False

    if target_format == "avif" and not HAS_AVIF:
        print("❌ 轉換失敗: 需要安裝 pillow-avif-plugin 才能輸出 AVIF 格式")
        return False
    if target_format == "jxl" and not HAS_JXL:
        print("❌ 轉換失敗: 需要安裝 pillow-jpegxl-plugin 才能輸出 JPEG XL 格式")
        return False
    if target_format in {"heic", "heif"} and not HAS_HEIC:
        print("❌ 轉換失敗: 需要安裝 pillow-heif 才能輸出 HEIC/HEIF 格式")
        return False

    save_kwargs = get_default_save_kwargs(target_format)
    if save_options:
        save_kwargs.update(save_options)

    try:
        with Image.open(source) as img:
            img = img.convert("RGB") if save_format == "JPEG" else img
            img.save(target_path, save_format, **save_kwargs)
        print(f"✅ 轉換成功: {source.name} -> {target_path.name}")
        return True
    except Exception as exc:
        print(f"❌ 轉換失敗: {source.name} -> {exc}")
        return False


def main() -> None:
    print("🖼️ 圖片格式轉換工具")
    print("===================================")
    if not HAS_AVIF:
        print("ℹ️ 如需處理 AVIF，請先安裝 pillow-avif-plugin")
    if not HAS_JXL:
        print("ℹ️ 如需處理 JPEG XL，請先安裝 pillow-jpegxl-plugin")
    if not HAS_HEIC:
        print("ℹ️ 如需處理 HEIC/HEIF，請先安裝 pillow-heif")

    # 取得來源路徑
    raw_path = input("請輸入檔案或資料夾路徑（預設為當前資料夾 .）: ").strip() or "."
    source_path = Path(raw_path).expanduser().resolve()

    if not source_path.exists():
        print(f"❌ 錯誤: 路徑不存在 -> {source_path}")
        return

    # 取得目標格式
    try:
        target_format = normalize_target_format(input("請輸入目標格式（例: png/jpg/webp/avif/jxl）: "))
    except ValueError as exc:
        print(f"❌ 錯誤: {exc}")
        return

    save_options: dict[str, object] = {}
    if prompt_yes_no("是否調整輸出畫質設定？[y/N]: "):
        save_options = prompt_save_options(target_format)

    # 取得輸出資料夾
    raw_output_dir = input("請輸入輸出資料夾（留空使用原位置）: ").strip()
    output_dir = Path(raw_output_dir).expanduser().resolve() if raw_output_dir else None

    # 是否覆蓋既有檔案
    overwrite_choice = input("若輸出檔已存在是否覆蓋？[y/N]: ").strip().lower() or "n"
    overwrite = overwrite_choice == "y"

    # 收集要轉換的圖片
    if source_path.is_file():
        images = [source_path] if source_path.suffix.lower() in SUPPORTED_INPUT_EXTS else []
    else:
        images = collect_images(source_path.rglob("*"))

    if not images:
        print("ℹ️ 找不到可轉換的圖片檔案")
        return

    if not HAS_AVIF and any(img.suffix.lower() == ".avif" for img in images):
        print("⚠️ 偵測到 AVIF 檔案，但尚未安裝 pillow-avif-plugin，可能無法成功讀取")
    if not HAS_JXL and any(img.suffix.lower() == ".jxl" for img in images):
        print("⚠️ 偵測到 JPEG XL 檔案，但尚未安裝 pillow-jpegxl-plugin，可能無法成功讀取")
    if not HAS_HEIC and any(img.suffix.lower() in {".heic", ".heif"} for img in images):
        print("⚠️ 偵測到 HEIC/HEIF 檔案，但尚未安裝 pillow-heif，可能無法成功讀取")

    print(f"找到 {len(images)} 個檔案，開始轉換...")

    success = 0
    for image_path in images:
        if convert_image(image_path, target_format, output_dir, overwrite, save_options):
            success += 1

    print(f"\n📊 轉換完成: 成功 {success}/{len(images)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程式已取消")
    except Exception as exc:
        print(f"\n❌ 發生未預期的錯誤: {exc}")
    finally:
        input("\n按 Enter 鍵結束程式...")
