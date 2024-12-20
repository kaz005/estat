# Cursor 開発ルール

## 1. データ構造の確認プロセス

### 1.1 確認フロー
#### 新規データソース導入時の手順
1. 必要事項の確認とチェックリストの実施
   - データ形式（CSV, JSONなど）
   - 必須・任意項目の特定
   - 文字コードとファイル構成の確認
2. 初期確認結果をマネージャーに提出し、承認を得る
3. 承認後、結果をチーム内で共有

### 1.2 確認結果の記録・保存
- 全確認内容はナレッジベースに記録
- 再利用可能な形式での保存

## 2. 実装前の基本確認事項

### 2.1 段階的な実装と確認
#### チェックリスト
- ファイルパスの存在確認
- 圧縮ファイルの展開と中身確認
- エラーハンドリングコードの事前実装
- 実データでの動作確認

#### 注意事項
- 初期段階では限定的な範囲でテストを実施
- 進捗に応じて段階的に拡張
- 大きな変更が必要な場合は、人間の承認を必須とする

## 3. エラーハンドリングとデバッグ

### 3.1 エラー処理の優先順位
1. 致命的エラー（クリティカルエラー）
   - プロセスを停止
   - 即座に原因をログに記録
2. 非致命的エラー
   - 処理を続行
   - 問題をログに記録

### 3.2 デバッグ手順
- 実データを使用した段階的なデバッグ
- エラー発生時の環境（状態・入力値）を詳細に記録
- デバッグ結果をチームで共有
- ナレッジベースに反映

## 4. データ処理の基本原則

### 4.1 データクリーニングの優先順位
- 妥当性チェック（例: 数値型データの範囲確認）
- 欠損値や異常値の除外または補完
- 必須項目の欠落確認

### 4.2 フィルタリングの段階的実施
- データソース側での可能な限りの前処理
- 必要に応じて、ユーザーインターフェースでのフィルタリングを設計

## 5. ユーザビリティとパフォーマンス

### 5.1 ユーザビリティ強化
- 初心者でも理解できるエラーメッセージの提供
- ユーザーが選択可能な直感的なインターフェースの提供

### 5.2 パフォーマンス最適化
- 大規模データ処理時の事前キャッシュ活用
- 必要なデータのみの読み込み

## 6. 自動化と人間の確認バランス

### 6.1 自動化可能なタスク
- 繰り返し作業
  - データ形式の妥当性確認
  - 文字コードチェック
- 初期エラーログの記録と報告

### 6.2 人間の確認が必要なタスク
- 新規データソースの導入時
- 重大な仕様変更やフォーマット変更の際の影響評価

## 7. 品質管理とドキュメント

### 7.1 品質管理
- エッジケースへの対応状況をリストアップし、定期的にレビュー
- 開発終了前に一貫性と正確性をチームで検証

### 7.2 ドキュメント管理
- 実装の変更履歴やトラブルシューティング記録をナレッジベースに反映
- ドキュメントの更新をタスクに組み込み、運用効率化を図る

## 付録: 簡略化チェックリスト

### 重要ポイント一覧
1. データ確認
   - データ形式とフォーマット確認
   - 必須・任意項目の特定
2. 実装前
   - ファイル存在確認
   - 初期エラー処理の準備
3. エラーハンドリング
   - 重大エラーの即時対応
   - 非致命的エラーのログ記録
4. データクリーニング
   - 異常値の除外
   - フィルタリングの実施
5. 品質とパフォーマンス
   - 一貫性と正確性の確保
   - ユーザーフレンドリーな設計

## 改善のポイント
このルールは状況に応じて柔軟に変更可能です。必要に応じて具体的なケースに合わせて拡張や修正を行ってください。