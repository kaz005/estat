import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

def load_excel_data(file_path: Path) -> pd.DataFrame:
    """Excelファイルを読み込む関数"""
    try:
        # データの読み込み（2行目をヘッダーとして使用）
        df = pd.read_excel(file_path, skiprows=1)
        
        # カラム名を設定
        df.columns = ['団体コード', '都道府県名', '市区町村名', '性別'] + [
            '総数',
            '0歳～4歳', '5歳～9歳', '10歳～14歳', '15歳～19歳',
            '20歳～24歳', '25歳～29歳', '30歳～34歳', '35歳～39歳',
            '40歳～44歳', '45歳～49歳', '50歳～54歳', '55歳～59歳',
            '60歳～64歳', '65歳～69歳', '70歳～74歳', '75歳～79歳',
            '80歳～84歳', '85歳～89歳', '90歳～94歳', '95歳～99歳',
            '100歳以上'
        ]
        
        # データ型の変換
        numeric_columns = [col for col in df.columns if '歳' in col or col == '総数']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 団体コードの正規化
        df['団体コード'] = df['団体コード'].astype(str).str.replace('-', '').str.zfill(6)
        
        return df
    except Exception as e:
        raise Exception(f"データの読み込みに失敗しました: {str(e)}")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """データのクリーニングを行う関数"""
    # 欠損値の処理
    df = df.dropna(subset=['団体コード', '都道府県名', '市区町村名', '性別', '総数'])
    
    # 性別の正規化
    df['性別'] = df['性別'].str.strip()
    
    return df

def filter_data(
    df: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """データのフィルタリングを行う関数"""
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if value is not None:
            filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df

def get_numerical_columns(df: pd.DataFrame) -> list:
    """数値型のカラムリストを取得する関数"""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> list:
    """カテゴリ型のカラムリストを取得する関数"""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def get_date_columns(df: pd.DataFrame) -> list:
    """日付型のカラムリストを取得する関数"""
    return df.select_dtypes(include=['datetime64']).columns.tolist() 