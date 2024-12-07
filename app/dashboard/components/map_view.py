import json
import folium
from pathlib import Path
import streamlit as st
from streamlit_folium import folium_static
import logging
from typing import Dict, Any

# ロガーの設定
logger = logging.getLogger(__name__)

def load_city_coordinates() -> Dict[str, Dict[str, Any]]:
    """市区町村の座標データを読み込む"""
    json_path = Path(__file__).parent.parent / 'data' / 'city_coordinates_with_codes.json'
    logger.info(f"Loading coordinates from: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            coordinates_data = json.load(f)
            
            # データを都道府県ごとに整理
            organized_data = {}
            for code, city_data in coordinates_data.items():
                pref_name = city_data['prefecture']
                if pref_name not in organized_data:
                    organized_data[pref_name] = {}
                
                organized_data[pref_name][code] = {
                    'name': city_data['city'],
                    'lat': city_data['lat'],
                    'lng': city_data['lng']
                }
            
            return organized_data
    except Exception as e:
        logger.error(f"Failed to load coordinates: {str(e)}")
        st.error("座標データの読み込みに失敗しました。管理者に連絡してください。")
        return {}

def create_map_view(df, prefecture, selected_codes=None, selected_value='総人口'):
    """地図表示コンポーネントを作成"""
    # デバッグ情報：データフレームのカラム名と内容を確認
    logger.info(f"データフレームのカラム: {df.columns.tolist()}")
    logger.info(f"データフレームのサンプル:\n{df[['団体コード', '都道府県名', '市区町村名']].head()}")
    
    # 座標データを読み込む
    coordinates_data = load_city_coordinates()
    
    if not coordinates_data:
        st.error("座標データが利用できません。")
        return None
    
    # デバッグ情報：座標データの内容を確認
    logger.info(f"座標データの都道府県: {list(coordinates_data.keys())}")
    if prefecture in coordinates_data:
        logger.info(f"座標データのサンプル（{prefecture}）: {list(coordinates_data[prefecture].keys())[:5]}")
    
    if prefecture not in coordinates_data:
        st.error(f"選択された都道府県（{prefecture}）��座標データが見つかりません。")
        return None

    # デバッグ情報の表示
    logger.info(f"データフレームの行数: {len(df)}")
    logger.info(f"選択された都道府県: {prefecture}")
    if selected_codes:
        logger.info(f"選択された団体コード: {selected_codes}")

    # デフォルトの中心座標（日本の中心あたり）
    center_lat, center_lng = 36.0, 136.0
    zoom_start = 5
    
    # 都道府県が選択されている場合は、その都道府県の中心に移動
    if prefecture and prefecture in coordinates_data:
        prefecture_coords = coordinates_data[prefecture]
        if prefecture_coords:
            lats = [coord['lat'] for coord in prefecture_coords.values()]
            lngs = [coord['lng'] for coord in prefecture_coords.values()]
            if lats and lngs:
                center_lat = sum(lats) / len(lats)
                center_lng = sum(lngs) / len(lngs)
                zoom_start = 8

    # 地図を作成
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_start,
        tiles="OpenStreetMap"
    )

    # 年齢区分の定義
    value_columns = {
        '総人口': '総数',
        '20歳未満': ['0歳～4歳', '5歳～9歳', '10歳～14歳', '15歳～19歳'],
        '30-60代': ['30歳～34歳', '35歳～39歳', '40歳～44歳', '45歳～49歳', 
                  '50歳～54歳', '55歳～59歳', '60歳～64歳', '65歳～69歳'],
        '70歳以上': ['70歳～74歳', '75歳～79歳', '80歳～84歳', '85歳～89歳', 
                  '90歳～94歳', '95歳～99歳', '100歳以上']
    }

    # データフレームに含まれる市区町村をマッピング
    if not df.empty and prefecture:
        try:
            # 選択された市区町村のデータをフィルタリング
            prefecture_mask = df['都道府県名'].astype(str) == prefecture
            gender_mask = df['性別'].astype(str) == '計'
            
            filtered_df = df[prefecture_mask & gender_mask]
            
            # デバッグ情報：フィルタリング後のデータを確認
            logger.info(f"都道府県でフィルタリング後のデータ件数: {len(filtered_df)}")
            logger.info(f"フィルタリング後のデータサンプル:\n{filtered_df[['団体コード', '市区町村名']].head()}")
            
            if selected_codes:
                filtered_df = filtered_df[filtered_df['団体コード'].isin(selected_codes)]
                logger.info(f"選択された団体コード: {selected_codes}")

            # デバッグ情報
            logger.info(f"最終的なフィルタリング後のデータ行数: {len(filtered_df)}")
            
            # 最大人口を取得して円の大きさを調整
            max_population = 0
            for _, row in filtered_df.iterrows():
                if selected_value == '総人口':
                    value = float(row[value_columns[selected_value]])
                else:
                    value = sum(float(row[col]) for col in value_columns[selected_value])
                max_population = max(max_population, value)
            
            logger.info(f"最大人口: {max_population}")
            
            # 市区町村ごとにマーカーを追加
            markers_added = 0
            for _, row in filtered_df.iterrows():
                code = str(row['団体コード']).zfill(6)
                city_name = row['市区町村名']
                
                # 値の計算
                if selected_value == '総人口':
                    value = float(row[value_columns[selected_value]])
                else:
                    value = sum(float(row[col]) for col in value_columns[selected_value])
                
                # 座標の取得
                if code in coordinates_data[prefecture]:
                    coord = coordinates_data[prefecture][code]
                    # 円の半径を人口に応じて調整（最小5、最大20）
                    radius = 5 + (value / max_population * 15) if max_population > 0 else 5
                    
                    # ツールチップとポップアップの内容を作成
                    tooltip = f"{city_name}: {int(value):,}人"
                    popup_html = f"""
                        <div style='width:200px'>
                            <b>{city_name}</b><br>
                            {selected_value}: {int(value):,}人
                        </div>
                    """
                    
                    # マーカーを追加
                    folium.CircleMarker(
                        location=[coord['lat'], coord['lng']],
                        radius=radius,
                        color='blue',
                        fill=True,
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=tooltip
                    ).add_to(m)
                    markers_added += 1
                else:
                    logger.warning(f"座標が見つかりません: {city_name} (コード: {code})")
            
            logger.info(f"追加されたマーカーの数: {markers_added}")
        
        except Exception as e:
            logger.error(f"データ処理中にエラーが発生しました: {str(e)}")
            st.error(f"データの処理中にエラーが発生しました: {str(e)}")
            return None

    return m

def display_map_section(df, prefecture, selected_codes=None):
    """地図セクションを表示"""
    st.header("地図表示")
    
    if df.empty:
        st.warning("データが読���込まれていません。")
        return
    
    if not prefecture:
        st.warning("都道府県を選択してください。")
        return
    
    # 表示する指標の選択
    value_options = ['総人口', '20歳未満', '30-60代', '70歳以上']
    selected_value = st.selectbox(
        "表示する指標を選択",
        value_options,
        index=0
    )
    
    # 地図の作成と表示
    m = create_map_view(df, prefecture, selected_codes, selected_value)
    if m is not None:
        folium_static(m)
        
        # 凡例の表示
        st.markdown("""
        **凡例：**
        - 円の大きさは選択した指標の値に比例します
        - 円をクリックすると詳細情報を確認できます
        """)
    else:
        st.error("地図の表示に失敗しました。")