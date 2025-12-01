import os
from pathlib import Path
from markitdown import MarkItDown  # 需要先安裝: pip install markitdown

# 注意：此程式需要安裝 markitdown 套件
# 安裝方法：pip install markitdown
# markitdown 支援多種格式，包括 PDF, DOCX, PPTX, XLSX, HTML, TXT, RTF, EPUB, 圖片等

def convert_file_to_md(input_file, output_file=None):
    """將支援的檔案格式轉換為 markdown 檔案"""
    
    input_path = Path(input_file)
    
    # 如果未提供輸出檔案，則使用相同名稱但擴展名為 .md
    if output_file is None:
        output_file = input_path.with_suffix('.md')
    else:
        output_file = Path(output_file)
    
    print(f"正在轉換 {input_path} 為 {output_file}...")
    
    try:
        # 使用 markitdown 進行轉換
        md = MarkItDown()
        result = md.convert(str(input_path))
        text = result.text_content
        
        # 寫入 Markdown 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ 轉換成功: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        return False

def batch_convert(folder_path):
    """批次轉換資料夾中的所有支援檔案"""
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"❌ 錯誤: {folder_path} 不是有效的資料夾路徑")
        return
    
    # 支援的檔案格式
    supported_extensions = [
        '*.pdf', '*.docx', '*.pptx', '*.xlsx', '*.html', '*.htm',
        '*.txt', '*.rtf', '*.epub', '*.png', '*.jpg', '*.jpeg',
        '*.gif', '*.bmp', '*.tiff', '*.csv', '*.json'
    ]
    
    # 尋找所有支援的檔案
    files = []
    for ext in supported_extensions:
        files.extend(list(folder.glob(ext)))
    
    if not files:
        print(f"ℹ️ 在 {folder_path} 中未找到支援的文件")
        return
    
    print(f"找到 {len(files)} 個支援的文件")
    
    # 轉換每個檔案
    success_count = 0
    for file in files:
        if convert_file_to_md(file):
            success_count += 1
    
    print(f"\n📊 轉換統計: 成功 {success_count}/{len(files)}")

def main():
    """主程式"""
    
    # 選擇模式：單一檔案或批次處理
    print("📝 多格式轉 Markdown 轉換工具")
    print("===================================")
    print("支援格式: PDF, DOCX, PPTX, XLSX, HTML, TXT, RTF, EPUB, 圖片等")
    print("1. 轉換單一檔案")
    print("2. 轉換資料夾中的所有檔案")
    choice = input("請選擇操作模式 [1/2]: ").strip() or "1"
    
    if choice == "1":
        # 單一檔案模式
        file_path = input("請輸入檔案路徑: ").strip()
        if not file_path:
            print("❌ 錯誤: 未提供檔案路徑")
            return
        
        if not os.path.isfile(file_path):
            print(f"❌ 錯誤: 檔案不存在: {file_path}")
            return
        
        # 可選輸出檔案名稱
        output_path = input("請輸入輸出 Markdown 檔案路徑 (留空則使用相同名稱): ").strip() or None
        convert_file_to_md(file_path, output_path)
    
    elif choice == "2":
        # 批次處理模式
        folder_path = input("請輸入包含檔案的資料夾路徑: ").strip()
        if not folder_path:
            print("❌ 錯誤: 未提供資料夾路徑")
            return
        
        batch_convert(folder_path)
    
    else:
        print("❌ 無效的選擇")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程式已取消")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
    finally:
        input("\n按 Enter 鍵結束程式...")