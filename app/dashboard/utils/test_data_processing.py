import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
from app.dashboard.utils.constants import AGE_ORDER, GRAPH_COLORS
from app.dashboard.data.loader import (
    load_population_data,
    get_municipalities_by_prefecture,
    get_municipality_data
)

def test_municipality_data_retrieval(df: pd.DataFrame) -> None:
    """市区町村データ取得のテストを行う関数"""
    print("\n=== 市区町村データ取得テスト ===")
    try:
        # テスト用の都道府県を選択（三重県）
        test_prefecture = "三重県"
        print(f"\n1. {test_prefecture}の市区町村データ取得テスト:")
        
        # 市区町村一覧の取得
        municipalities_df = get_municipalities_by_prefecture(df, test_prefecture)
        print(f"取得された市区町村数: {len(municipalities_df)}")
        print("\nカラム一覧:")
        print(municipalities_df.columns.tolist())
        print("\n最初の5件:")
        print(municipalities_df.head())
        
        # 特定の市のデータ取得テスト
        test_cities = municipalities_df['団体コード'].head(3).tolist()
        print(f"\n2. 選択された市区町村のデータ取得テスト（{len(test_cities)}件）:")
        city_data = get_municipality_data(df, test_cities)
        print(f"取得されたデータ件数: {len(city_data)}")
        print("\n市区町村名と総人口:")
        for _, row in city_data.iterrows():
            print(f"{row['市区町村名']}: {int(row['総数']):,}人")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def test_age_group_aggregation(df: pd.DataFrame) -> None:
    """年齢区分の集計処理をテストする関数"""
    print("\n=== 年齢区分集計テスト ===")
    try:
        # テスト用の市区町村を選択
        test_city = df[
            (df['都道府県名'] == '東京都') & 
            (df['市区町村名'] == '新宿区') & 
            (df['性別'] == '計')
        ].iloc[0]
        
        # 年齢区分の定義
        age_groups = {
            '20代': ['20歳～24歳', '25歳～29歳'],
            '30代': ['30歳～34歳', '35歳～39歳'],
            '40代': ['40歳～44歳', '45歳～49歳'],
            '50代': ['50歳～54歳', '55歳～59歳'],
            '60代': ['60歳～64歳', '65歳～69歳'],
            '70歳以上': ['70歳～74歳', '75歳～79歳', '80歳～84歳', '85歳～89歳', 
                     '90歳～94歳', '95歳～99歳', '100歳以上']
        }
        
        # 各年齢区分の人口を計算
        results = {}
        total_population = 0
        for group, columns in age_groups.items():
            population = sum(test_city[col] for col in columns)
            total_population += population
            results[group] = population
        
        # 結果の表示
        print(f"市区町村: {test_city['市区町村名']}")
        print("\n年齢区分別人口:")
        for group, population in results.items():
            percentage = (population / total_population) * 100
            print(f"{group}: {int(population):,}人 ({percentage:.1f}%)")
        print(f"合計: {int(total_population):,}人")
        
        # 合計が総数と一致することを確認
        expected_total = sum(test_city[col] for col in [col for col in test_city.index if '歳' in col])
        print(f"\n検証: 計算された合計と実際の総数の差: {abs(total_population - expected_total):.1f}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def test_data_filtering(df: pd.DataFrame) -> None:
    """データフィルタリング処理をテストする関数"""
    print("\n=== フィルタリングテスト ===")
    try:
        # 基本的なフィルタリング
        filters = {'性別': '計', '都道府県名': '東京都'}
        filtered_df = df[
            (df['性別'] == filters['性別']) & 
            (df['都道府県名'] == filters['都道府県名'])
        ]
        
        print(f"フィルタリング条件: {filters}")
        print(f"フィルタリング後のデータ件数: {len(filtered_df)}")
        print("\n最初の5件:")
        print(filtered_df[['都道府県名', '市区町村名', '総数']].head())
        
        # データの整合性チェック
        print("\nデータ整合性チェック:")
        print(f"- 性別が'計'以外のデータ: {len(filtered_df[filtered_df['性別'] != '計'])}")
        print(f"- 都道府県名が'東京都'以外のデータ: {len(filtered_df[filtered_df['都道府県名'] != '東京都'])}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def test_data_cleaning(df: pd.DataFrame) -> None:
    """データクリーニング処理をテストする関数"""
    print("\n=== データクリーニングテスト ===")
    try:
        # クリーニング前の状態
        print("クリーニング前:")
        print(f"- 総行数: {len(df)}")
        print(f"- 欠損値を含む行数: {len(df[df.isnull().any(axis=1)])}")
        
        # 団体コードの形式チェック
        invalid_codes = df[~df['団体コード'].str.match(r'^\d{6}$')]
        print(f"- 不正な形式の団体コード数: {len(invalid_codes)}")
        if len(invalid_codes) > 0:
            print("不正な団体コードの例:")
            print(invalid_codes['団体コード'].head())
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def run_all_tests() -> None:
    """全てのテストを実行する関数"""
    try:
        # データの読み込み
        file_path = Path('data/24nsnen.xlsx')
        df = load_population_data(file_path)
        
        # 各テストの実行
        test_data_cleaning(df)
        test_municipality_data_retrieval(df)  # 新しいテストを追加
        test_data_filtering(df)
        test_age_group_aggregation(df)
        
        print("\n=== 全てのテストが完了しました ===")
        
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    run_all_tests() 