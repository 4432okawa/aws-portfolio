# AWS Lambda S3 Trigger Function

このPython Lambda関数はS3バケットにアップロードされたファイルを処理します：
- **トリガー**: `yossy-input-bucket-20250503`へのS3ファイルアップロードで起動します。
- **機能**: ファイルを読み込み、テキストを大文字に変換し、`yossy-output-bucket-20250503/processed/`に保存します。
- **リージョン**: `us-west-2`に設定されています。

## 目的
AWS Lambda、Python、AWS CLI、およびTerraformを使用したサーバーレスアプリケーションの構築能力を示します。クラウドエンジニアリング役割に適した安全な設定でサーバーレスワークフローを自動化する能力を示します。

## ファイル
- `lambda_function.py`: S3イベントを処理するLambda関数コード
- `main.tf`: Terraformインフラストラクチャコード

## 使用方法
Terraformを使用してLambda関数をデプロイしテストするには、以下の手順に従ってください：

1. **AWS CLIとTerraformのインストールとSSOプロファイルの設定**:
   - AWS CLIを`https://aws.amazon.com/cli/`からインストール
   - Terraformを`https://www.terraform.io/downloads`からインストール
   - SSOを設定:
     ```cmd
     aws configure sso
     ```
   - 検証:
     ```cmd
     aws sts get-caller-identity --profile anagram-sso
     ```

2. **Terraform初期化と適用**:
   - Terraformディレクトリに移動:
     ```cmd
     cd aws-portfolio\terraform-s3
     ```
   - Lambda関数のコードを作成:
     ```cmd
     mkdir lambda_code
     cd lambda_code
     # lambda_function.pyを作成して保存
     ```
   - ZIP形式でパッケージ化:
     ```cmd
     powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath ..\function.zip -Force"
     cd ..
     ```
   - Terraformを初期化して適用:
     ```cmd
     terraform init
     terraform apply --var="profile=anagram-sso"
     ```

3. **関数のテスト**:
   - テストファイルを作成:
     ```cmd
     echo "This is a test file. Hello World!" | Out-File -Encoding ascii test2.txt
     ```
   - 入力バケットにアップロード:
     ```cmd
     aws s3 cp test2.txt s3://yossy-input-bucket-20250503/ --profile anagram-sso
     ```
   - 出力を確認:
     ```cmd
     aws s3 ls s3://yossy-output-bucket-20250503/processed/ --profile anagram-sso
     aws s3 cp s3://yossy-output-bucket-20250503/processed/test2.txt processed_test.txt --profile anagram-sso
     type processed_test.txt
     ```
   - 期待される出力: `THIS IS A TEST FILE. HELLO WORLD!`

## コード例（Lambda関数）
```python
import json
import boto3
import logging
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # 入力検証: イベントの構造を確認
        if not event.get('Records') or len(event['Records']) == 0:
            logger.error("Invalid event structure: no Records found")
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid event structure')
            }
            
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # 入力値のサニタイズと検証
        if not bucket or not key:
            logger.error("Missing bucket name or object key")
            return {
                'statusCode': 400,
                'body': json.dumps('Missing bucket name or object key')
            }
            
        logger.info(f"Processing file: {key} from bucket: {bucket}")

        try:
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Error retrieving object from S3: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps('Error retrieving file from S3')
            }

        upper_content = content.upper()

        # 環境変数の安全な取得
        output_bucket = os.environ.get('OUTPUT_BUCKET')
        if not output_bucket:
            output_bucket = 'yossy-output-bucket-20250503'
            logger.warning(f"OUTPUT_BUCKET environment variable not set, using default: {output_bucket}")
            
        output_key = f"processed/{key}"
        
        try:
            s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=upper_content)
        except ClientError as e:
            logger.error(f"Error saving object to S3: {str(e)}")
            return {
                'statusCode': 500,
                'body': json.dumps('Error saving processed file to S3')
            }

        logger.info(f"Saved to {output_bucket}/{output_key}")
        return {
            'statusCode': 200,
            'body': json.dumps('File processed successfully')
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing file: {str(e)}')
        }
```

## 注意事項
- エンコーディングの問題が発生した場合は、ファイルをASCIIまたはUTF-8でエンコードしてください。
- Lambda関数のコードを変更する場合は、新しいZIPファイルを作成し、再度Terraformを適用してください。
- テスト完了後にリソースを削除するには `terraform destroy --var="profile=anagram-sso"` を実行してください。

## セキュリティ
- 環境変数を使用して出力バケット名を安全に取得しています。
- IAMロールは最小権限の原則に従ってカスタムS3ポリシーを使用しています。
- すべてのバケットはパブリックアクセスがブロックされ、暗号化が有効になっています。