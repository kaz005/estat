import os
from pathlib import Path
import streamlit as st
from app.dashboard.main import run_dashboard

def main():
    # プロジェクトのルートディレクトリを取得
    root_dir = Path(__file__).parent
    # Excelファイルのパスを構築
    excel_path = root_dir / 'data' / '24nsnen.xlsx'
    
    st.set_page_config(
        page_title="📊 統計データ分析ダッシュボード",
        page_icon="📊",
        layout="wide"
    )
    
    run_dashboard(str(excel_path))

if __name__ == "__main__":
    main() 