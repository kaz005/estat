import streamlit as st
import pandas as pd
from app.dashboard.data.loader import load_population_data, get_municipalities_by_prefecture
from app.dashboard.components.map_view import display_map_section
from app.dashboard.components.charts import display_age_analysis, display_voting_trend

def run_dashboard(excel_path: str):
    """メインのダッシュボード処理"""
    try:
        # データの読み込み
        df = load_population_data(excel_path)
        
        # タイトルの設定
        st.title("📊 統計データ分析ダッシュボード")
        
        # サイドバーの設定
        st.sidebar.header("データフィルター")
        
        # 都道府県選択
        prefecture = st.sidebar.selectbox(
            "都道府県を選択してください",
            sorted(df['都道府県名'].unique())
        )
        
        # 市区町村の取得
        municipalities_df = get_municipalities_by_prefecture(df, prefecture)
        
        # 市区町村の選択肢を作成（団体コードと市区町村名の対応）
        municipality_options = {
            f"{row['市区町村名']}": row['団体コード']
            for _, row in municipalities_df.iterrows()
        }
        
        # デフォルトの選択（最初の3つ）
        default_selection = list(municipality_options.keys())[:3] if municipality_options else []
        
        # 市区町村の複数選択
        selected_municipality_labels = st.sidebar.multiselect(
            "市区町村を選択（複数選択可）",
            options=list(municipality_options.keys()),
            default=default_selection,
            key=f"municipalities_{prefecture}"
        )
        
        # 選択された市区町村の団体コードを取得
        selected_codes = [
            municipality_options[label]
            for label in selected_municipality_labels
        ]
        
        # 選択された市区町村のデータを取得
        selected_data = df[
            (df['都道府県名'] == prefecture) & 
            (df['団体コード'].isin(selected_codes)) &
            (df['性別'] == '計')
        ]
        
        # タブの作成
        tab1, tab2, tab3 = st.tabs([
            "🗺️ 地理的分布",
            "📊 年齢構成分析",
            "🗳️ 投票傾向分析"
        ])
        
        # 地理的分布タブ
        with tab1:
            if selected_codes:
                display_map_section(df, prefecture, selected_codes)
            else:
                st.warning("市区町村を選択してください。")
        
        # 年齢構成分析タブ
        with tab2:
            if selected_codes:
                display_age_analysis(selected_data, prefecture)
            else:
                st.warning("市区町村を選択してください。")
        
        # 投票傾向分析タブ
        with tab3:
            if selected_codes:
                display_voting_trend(selected_data, prefecture)
            else:
                st.warning("市区町村を選択してください。")
            
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.error(f"詳細: {type(e).__name__}")

if __name__ == "__main__":
    run_dashboard("data/24nsnen.xlsx")