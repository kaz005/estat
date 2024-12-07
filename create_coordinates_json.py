import os
import json
import glob
import time
from typing import Dict, Tuple, List
from tqdm import tqdm
from datetime import datetime

# 政令指定都市のコードリスト（2023年1月時点）
DESIGNATED_CITIES = {
    "札幌市": "01100", "仙台市": "04100", "さいたま市": "11100", "千葉市": "12100",
    "横浜市": "14100", "川崎市": "14130", "相模原市": "14150", "新潟市": "15100",
    "静岡市": "22100", "浜松市": "22130", "名古屋市": "23100", "京都市": "26100",
    "大阪市": "27100", "堺市": "27140", "神戸市": "28100", "岡山市": "33100",
    "広島市": "34100", "北九州市": "40100", "福岡市": "40130", "熊本市": "43100"
}

# 除外するエリアのキーワード
EXCLUDE_KEYWORDS = [
    "埋立地", "境界地", "所属未定地", "岩", "列岩", "河口部", "地先", "沖", "海",
    "湾", "水道", "灘", "堆", "瀬", "干潟"
]

class ProgressCounter:
    def __init__(self):
        self.start_time = time.time()
        self.counts = {
            "total": 0,
            "processed": 0,
            "skipped": 0,
            "error": 0
        }
    
    def update(self, status: str):
        self.counts[status] = self.counts.get(status, 0) + 1
        self.counts["total"] = self.counts["processed"] + self.counts["skipped"] + self.counts["error"]
    
    def get_progress(self) -> str:
        elapsed = time.time() - self.start_time
        return (f"処理: {self.counts['processed']:,}件 "
                f"スキップ: {self.counts['skipped']:,}件 "
                f"エラー: {self.counts['error']:,}件 "
                f"(経過時間: {elapsed:.1f}秒)")

def is_valid_municipality(name: str, code: str) -> bool:
    """市区町村名が有効かどうかをチェック"""
    if any(keyword in name for keyword in EXCLUDE_KEYWORDS):
        return False
    return bool(code and len(code) == 5)

def get_municipality_type(name: str) -> str:
    """市区町村の種別を判定"""
    if "区" in name:
        return "ward"
    elif "市" in name:
        return "city"
    elif "町" in name:
        return "town"
    elif "村" in name:
        return "village"
    return "other"

def calculate_centroid(coords: List) -> Tuple[float, float]:
    """ポリゴンの重心を計算"""
    try:
        if isinstance(coords[0][0][0], list):
            coords = coords[0]
        points = coords[0]
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)
    except:
        return None, None

def process_geojson(file_path: str) -> Dict:
    """GeoJSONファイルを処理"""
    print(f"\n処理開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ファイル: {os.path.basename(file_path)}")
    
    counter = ProgressCounter()
    municipalities = {}
    
    # ファイル読み込み
    print("\nステップ1: GeoJSONファイル読み込み中...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    features = data.get('features', [])
    print(f"読み込み完了: {len(features):,}件のデータ")
    
    # データ処理
    print("\nステップ2: データ処理中...")
    for feature in tqdm(features, desc="進捗"):
        try:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            code = properties.get('N03_007')
            name = properties.get('N03_004')
            
            # 政令指定都市の区は別途処理
            if code[:5] in DESIGNATED_CITIES.values():
                counter.update("skipped")
                continue
            
            # 無効な市区町村はスキップ
            if not is_valid_municipality(name, code):
                counter.update("skipped")
                continue
            
            # 座標の取得と処理
            coords = geometry.get('coordinates', [])
            if coords:
                if geometry['type'] == 'MultiPolygon':
                    lng, lat = calculate_centroid(coords[0])
                elif geometry['type'] == 'Polygon':
                    lng, lat = calculate_centroid([coords])
                else:
                    counter.update("skipped")
                    continue
                
                if lng is None or lat is None:
                    counter.update("skipped")
                    continue
                
                # データを保存
                municipalities[code] = {
                    "name": name,
                    "type": get_municipality_type(name),
                    "lat": lat,
                    "lng": lng
                }
                counter.update("processed")
                
                # 進捗を定期的に表示
                if counter.counts["total"] % 1000 == 0:
                    print(f"\n{counter.get_progress()}")
            
        except Exception as e:
            print(f"\n警告: {name}({code})の処理中にエラー: {str(e)}")
            counter.update("error")
    
    # 処理結果の表示
    print(f"\n処理完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"最終結果: {counter.get_progress()}")
    print(f"有効な市区町村数: {len(municipalities):,}件")
    
    return municipalities

def main():
    try:
        print("市区町村座標データ生成プログラム")
        print("=" * 50)
        
        # GeoJSONファイルの検索
        geojson_files = glob.glob('data/*.geojson')
        if not geojson_files:
            raise FileNotFoundError("GeoJSONファイルが見つかりません")
        
        # データ処理
        municipalities = process_geojson(geojson_files[0])
        
        # 結果の保存
        output_path = 'city_coordinates.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(municipalities, f, ensure_ascii=False, indent=2)
        
        print(f"\nファイル保存完了: {output_path}")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 