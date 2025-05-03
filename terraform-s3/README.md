# AWS Lambda S3 Trigger Function

This Python Lambda function:
- Triggers on S3 file uploads
- Reads the file, converts text to uppercase
- Saves the result to another S3 bucket

## Usage
1. Deploy to AWS Lambda with S3 trigger configured.
2. Ensure IAM role has S3 read/write permissions.

# AWS Lambda S3 トリガー関数

この Python Lambda 関数は以下の機能を実行します。
- S3 ファイルのアップロード時にトリガーします。
- ファイルを読み取り、テキストを大文字に変換します。
- 結果を別の S3 バケットに保存します。

## 使用方法
1. S3 トリガーを設定して AWS Lambda にデプロイします。
2. IAM ロールに S3 の読み取り/書き込み権限があることを確認します。