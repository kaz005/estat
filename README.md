# e-Stat データ可視化プロジェクト

e-Statのデータを処理・可視化するためのPythonプロジェクトです。

## 機能

- 統計データの分析・可視化
- 地理空間データの処理
- インタラクティブなダッシュボード表示

## セットアップ

1. リポジトリをクローン:
```bash
git clone https://github.com/kaz005/estat.git
cd estat
```

2. 仮想環境を作成してアクティベート:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows
```

3. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 地理データのダウンロード:
```bash
python download_gml.py
```

2. 座標データの生成:
```bash
python create_coordinates_json.py
```

3. ダッシュボードの起動:
```bash
streamlit run run.py
```

## データについて

- データディレクトリ（`data/`）は.gitignoreに含まれています
- 必要なデータファイルは自動的にダウンロードされます
- 実行前に必要なデータファイルが`data/`ディレクトリに配置されていることを確認してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
