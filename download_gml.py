import os
import requests
import zipfile
from typing import Optional
from tqdm import tqdm

def download_file(url: str, save_path: str) -> Optional[str]:
    """
    URLからファイルをダウンロード（進捗バー付き）
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # ファイルサイズを取得
        total_size = int(response.headers.get('content-length', 0))
        
        # プログレスバーの設定
        progress_bar = tqdm(
            total=total_size,
            unit='iB',
            unit_scale=True,
            desc='ダウンロード中'
        )
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                progress_bar.update(size)
        
        progress_bar.close()
        return save_path
    except Exception as e:
        print(f"ダウンロード中にエラーが発生しました: {str(e)}")
        return None

def extract_zip(zip_path: str, extract_path: str) -> None:
    """
    ZIPファイルを解凍（進捗表示付き）
    """
    try:
        print("解凍を開始します...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # ファイル一覧を取得
            files = zip_ref.namelist()
            
            # 各ファイルを解凍
            for file in tqdm(files, desc='解凍中'):
                zip_ref.extract(file, extract_path)
                
        print(f"解凍が完了しました: {extract_path}")
    except Exception as e:
        print(f"解凍中にエラーが発生しました: {str(e)}")

def main():
    # 国土数値情報のURL（最新の行政区域データ）
    url = "https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2023/N03-20230101_GML.zip"
    
    print("処理を開始します...")
    
    # ダウンロード先のディレクトリを作成
    os.makedirs("data", exist_ok=True)
    print("データディレクトリを確認しました")
    
    # ZIPファイルをダウンロード
    zip_path = os.path.join("data", "N03.zip")
    if download_file(url, zip_path):
        print("ダウンロードが完了しました")
        
        # ZIPファイルを解凍
        extract_zip(zip_path, "data")
        
        # ZIPファイルを削除
        os.remove(zip_path)
        print("一時ファイルを削除しました")
        print("全ての処理が完了しました")
    else:
        print("ダウンロードに失敗しました")

if __name__ == "__main__":
    main() 