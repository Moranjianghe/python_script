import os
from pathlib import Path
import pypandoc  # 需要先安裝: pip install pypandoc

# 注意：此程式需要安裝 pypandoc 套件
# 安裝方法：pip install pypandoc
# pypandoc 會自動下載和使用 pandoc

def convert_doc_to_md(input_file, output_file=None):
    """將 doc/docx 檔案轉換為 markdown 檔案"""
    
    input_path = Path(input_file)
    
    # 如果未提供輸出檔案，則使用相同名稱但擴展名為 .md
    if output_file is None:
        output_file = input_path.with_suffix('.md')
    else:
        output_file = Path(output_file)
    
    print(f"正在轉換 {input_path} 為 {output_file}...")
    
    # 設置轉換選項
    extra_args = [
        '--wrap=none',  # 不自動換行
        '--extract-media=./media'  # 提取圖片到 media 目錄
    ]
    
    try:
        # 使用 pypandoc 進行轉換
        pypandoc.convert_file(
            str(input_path),
            'markdown',
            outputfile=str(output_file),
            extra_args=extra_args
        )
        print(f"✅ 轉換成功: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        return False

def batch_convert(folder_path):
    """批次轉換資料夾中的所有 doc/docx 檔案"""
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"❌ 錯誤: {folder_path} 不是有效的資料夾路徑")
        return
    
    # 尋找所有 .doc 和 .docx 檔案
    doc_files = list(folder.glob('*.doc')) + list(folder.glob('*.docx'))
    
    if not doc_files:
        print(f"ℹ️ 在 {folder_path} 中未找到 Word 文件")
        return
    
    print(f"找到 {len(doc_files)} 個 Word 文件")
    
    # 轉換每個檔案
    success_count = 0
    for doc_file in doc_files:
        if convert_doc_to_md(doc_file):
            success_count += 1
    
    print(f"\n📊 轉換統計: 成功 {success_count}/{len(doc_files)}")

def main():
    """主程式"""
    
    # 選擇模式：單一檔案或批次處理
    print("📝 Word 轉 Markdown 轉換工具")
    print("===================================")
    print("1. 轉換單一檔案")
    print("2. 轉換資料夾中的所有檔案")
    choice = input("請選擇操作模式 [1/2]: ").strip() or "1"
    
    if choice == "1":
        # 單一檔案模式
        file_path = input("請輸入 Word 檔案路徑: ").strip()
        if not file_path:
            print("❌ 錯誤: 未提供檔案路徑")
            return
        
        if not os.path.isfile(file_path):
            print(f"❌ 錯誤: 檔案不存在: {file_path}")
            return
        
        # 可選輸出檔案名稱
        output_path = input("請輸入輸出 Markdown 檔案路徑 (留空則使用相同名稱): ").strip() or None
        convert_doc_to_md(file_path, output_path)
    
    elif choice == "2":
        # 批次處理模式
        folder_path = input("請輸入包含 Word 檔案的資料夾路徑: ").strip()
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
