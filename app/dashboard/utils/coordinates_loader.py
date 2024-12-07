import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import re

def parse_gml_coordinates(gml_content):
    """GMLファイルから座標データを抽出"""
    try:
        # XMLの名前空間を定義
        namespaces = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        root = ET.fromstring(gml_content)
        coordinates = {}
        
        # 市区町村ごとのデータを抽出
        for member in root.findall('.//ksj:POS', namespaces):
            try:
                # 市区町村名を取得
                city_name = member.find('.//ksj:cityName', namespaces).text
                # 座標を取得
                point = member.find('.//gml:pos', namespaces).text
                lat, lon = map(float, point.split())
                coordinates[city_name] = {'lat': lat, 'lng': lon}
            except Exception as e:
                print(f"市区町村データの解析エラー: {str(e)}")
                continue
        
        return coordinates
    except Exception as e:
        print(f"GML解析エラー: {str(e)}")
        return {}

def load_city_coordinates():
    """
    保存された市区町村の座標データを読み込む関数
    """
    geocode_dir = Path(__file__).parent.parent / 'data' / 'geocode'
    
    if not geocode_dir.exists():
        print(f"エラー: {geocode_dir} が見つかりません")
        return {}
    
    coordinates = {}
    prefecture_codes = {
        '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県',
        '05': '秋田県', '06': '山形県', '07': '福島県', '08': '茨城県',
        '09': '栃木県', '10': '群馬県', '11': '埼玉県', '12': '千葉県',
        '13': '東京都', '14': '神奈川県', '15': '新潟県', '16': '富山県',
        '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
        '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県',
        '25': '滋賀県', '26': '京都府', '27': '大阪府', '28': '兵庫県',
        '29': '奈良県', '30': '和歌山県', '31': '鳥取県', '32': '島根県',
        '33': '岡山県', '34': '広島県', '35': '山口県', '36': '徳島県',
        '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
        '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県',
        '45': '宮崎県', '46': '鹿児島県', '47': '沖縄県'
    }
    
    # 各ZIPファイルを処理
    for zip_path in geocode_dir.glob('P34-14_*_GML.zip'):
        try:
            # ファイル名から都道府県コードを抽出
            pref_code = re.search(r'P34-14_(\d{2})_', zip_path.name).group(1)
            prefecture = prefecture_codes.get(pref_code)
            
            if not prefecture:
                continue
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # GMLファイルを探す
                gml_files = [f for f in zip_ref.namelist() if f.endswith('.gml')]
                if not gml_files:
                    continue
                
                # 最初のGMLファイルを読み込む
                with zip_ref.open(gml_files[0]) as f:
                    gml_content = f.read().decode('utf-8')
                    prefecture_coords = parse_gml_coordinates(gml_content)
                    coordinates[prefecture] = prefecture_coords
        
        except Exception as e:
            print(f"ファイル処理エラー ({zip_path.name}): {str(e)}")
            continue
    
    return coordinates 