import os
import yt_dlp
import tempfile

def download_video(url, cookie_file=None, cookie_content=None):
    download_dir = os.path.expanduser('~/Downloads')
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    temp_cookie_file = None
    if cookie_file and os.path.isfile(cookie_file):
        ydl_opts['cookiefile'] = cookie_file
    elif cookie_content:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(cookie_content)
            temp_cookie_file = f.name
        ydl_opts['cookiefile'] = temp_cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"正在下載: {info['title']}")
            print(f"格式: {info['format_id']} - {info['resolution']}")
            ydl.download([url])
        print("下載成功！")
    except yt_dlp.DownloadError as e:
        print(f"下載失敗: {e}")
        print("建議：請確保 yt-dlp 是最新版本（運行 yt-dlp -U），並檢查 cookie 是否有效。")
        return False
    finally:
        if temp_cookie_file and os.path.exists(temp_cookie_file):
            os.unlink(temp_cookie_file)
    return True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"正在下載: {info['title']}")
            print(f"格式: {info['format_id']} - {info['resolution']}")
            ydl.download([url])
        print("下載成功！")
    except yt_dlp.DownloadError as e:
        print(f"下載失敗: {e}")
        return False
    return True

if __name__ == "__main__":
    url = input("請輸入視頻 URL：").strip()
    if not url:
        print("URL 不能為空。")
        exit(1)

    success = download_video(url)
    if not success:
        choice = input("下載失敗，可能需要 cookie。請選擇：1. 輸入 cookie 文件路徑 2. 直接輸入 cookie 內容（多行） 3. 跳過：").strip()
        if choice == '1':
            cookie_file = input("請輸入 cookie 文件路徑：").strip()
            if cookie_file:
                success = download_video(url, cookie_file=cookie_file)
        elif choice == '2':
            print("請輸入 cookie 內容，每行結束後按 Enter，輸入空行結束：")
            lines = []
            while True:
                line = input()
                if line == '':
                    break
                lines.append(line)
            cookie_content = '\n'.join(lines)
            if cookie_content.strip():
                success = download_video(url, cookie_content=cookie_content)
        else:
            print("跳過 cookie，下載失敗。")
        if not success and choice in ['1', '2']:
            print("仍然無法下載，請檢查 URL 或 cookie。")