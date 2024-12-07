import zipfile
import json
from pathlib import Path
import tempfile
import shutil
import re
import xml.etree.ElementTree as ET

def extract_coordinates_from_xml(xml_file):
    """XMLファイルから座標データを抽出"""
    try:
        # XMLファイルを読み込む
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # 名前空間を取得
        namespaces = {
            'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app',
            'gml': 'http://www.opengis.net/gml/3.2',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        
        # まず全ての座標ポイントを辞書に格納
        points = {}
        for point in root.findall('.//gml:Point', namespaces):
            point_id = point.get('{http://www.opengis.net/gml/3.2}id')
            pos = point.find('gml:pos', namespaces).text
            lat, lon = map(float, pos.split())
            points[point_id] = {'lat': lat, 'lng': lon}
        
        coordinates = {}
        # 市区町村の情報と座標を紐付け
        for facility in root.findall('.//ksj:LocalGovernmentOfficeAndPublicMeetingFacility', namespaces):
            try:
                # 役場（本庁舎）のみを対象とする
                office_type = facility.find('ksj:publicOfficeClassification', namespaces).text
                if office_type != '1':  # 1: 役場本庁舎
                    continue
                
                # 市区町村名を取得
                office_name = facility.find('ksj:publicOfficeName', namespaces).text
                city_name = office_name.replace('役場', '').replace('役所', '').strip()
                
                # 座標を取得
                position_ref = facility.find('ksj:position', namespaces).get('{http://www.w3.org/1999/xlink}href')
                point_id = position_ref.replace('#', '')
                
                if point_id in points:
                    coordinates[city_name] = points[point_id]
                    print(f"Found coordinates for {city_name}: {points[point_id]}")
            except Exception as e:
                print(f"市区町村データの解析エラー: {str(e)}")
                continue
        
        return coordinates
    except Exception as e:
        print(f"XML解析エラー: {str(e)}")
        return {}

def create_coordinates_database():
    """全国の市区町村の座標データを作成してJSONファイルに保存"""
    root_dir = Path(__file__).parent.parent.parent.parent
    geocode_dir = root_dir / 'app' / 'dashboard' / 'data' / 'geocode'
    output_file = root_dir / 'app' / 'dashboard' / 'data' / 'city_coordinates.json'
    
    print(f"Looking for geocode files in: {geocode_dir}")
    if not geocode_dir.exists():
        print(f"エラー: {geocode_dir} が見つかりません")
        return
    
    prefecture_codes = {
        '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県',
        '05': '秋田県', '06': '山形県', '07': '福島県', '08': '茨城県',
        '09': '栃木県', '10': '群馬県', '11': '埼玉県', '12': '千葉県',
        '13': '東京都', '14': '神奈川県', '15': '新潟県', '16': '富山県',
        '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
        '21': '岐阜県', '22': '静岡県', '23': '愛知���', '24': '三重県',
        '25': '滋賀県', '26': '京都府', '27': '大阪府', '28': '兵庫県',
        '29': '奈良県', '30': '和歌山県', '31': '鳥取県', '32': '島根県',
        '33': '岡山県', '34': '広島県', '35': '山口県', '36': '徳島県',
        '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
        '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県',
        '45': '宮崎県', '46': '鹿児島県', '47': '沖縄県'
    }
    
    coordinates = {}
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        for zip_path in geocode_dir.glob('P34-14_*_GML.zip'):
            try:
                pref_code = re.search(r'P34-14_(\d{2})_', zip_path.name).group(1)
                prefecture = prefecture_codes.get(pref_code)
                
                if not prefecture:
                    continue
                
                print(f"\nProcessing {prefecture} from {zip_path.name}...")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    print(f"Extracted files: {list(zip_ref.namelist())}")
                
                xml_files = list(temp_dir.glob('**/*.xml'))
                if not xml_files:
                    print(f"No XML files found in {zip_path.name}")
                    continue
                
                # KS-META-P34_14-XX.xmlを除外
                xml_files = [f for f in xml_files if not f.name.startswith('KS-META')]
                if not xml_files:
                    print(f"No valid XML files found in {zip_path.name}")
                    continue
                
                print(f"Found XML file: {xml_files[0]}")
                
                prefecture_coords = extract_coordinates_from_xml(xml_files[0])
                if prefecture_coords:
                    print(f"Found {len(prefecture_coords)} municipalities in {prefecture}")
                    coordinates[prefecture] = prefecture_coords
                else:
                    print(f"No coordinates found in {prefecture}")
                
                for file in temp_dir.glob('*'):
                    if file.is_file():
                        file.unlink()
            
            except Exception as e:
                print(f"ファイル処理エラー ({zip_path.name}): {str(e)}")
                continue
        
        print(f"\nTotal prefectures processed: {len(coordinates)}")
        print("Prefectures with data:", list(coordinates.keys()))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coordinates, f, ensure_ascii=False, indent=2)
        
        print(f"\n座標データを保存しました: {output_file}")
        
    finally:
        shutil.rmtree(temp_dir)
    
    return coordinates

if __name__ == '__main__':
    create_coordinates_database() 