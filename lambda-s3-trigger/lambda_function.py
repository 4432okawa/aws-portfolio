# Lambda function to process S3 file uploads and convert text to uppercase
import json
import boto3
import logging
import os
from botocore.exceptions import ClientError
import chardet  # エンコーディング検出用

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
            content_bytes = response['Body'].read()
            
            # エンコーディングを検出する（chardetがない場合は手動で追加）
            try:
                # chardetがない場合はこの部分をスキップ
                encoding_result = chardet.detect(content_bytes)
                encoding = encoding_result['encoding']
                logger.info(f"Detected encoding: {encoding}")
            except NameError:
                # chardetがインストールされていない場合のフォールバック
                # いくつかの一般的なエンコーディングで試行
                encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'ascii']
                content = None
                for enc in encodings_to_try:
                    try:
                        content = content_bytes.decode(enc)
                        logger.info(f"Successfully decoded with {enc}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # どのエンコーディングでも失敗した場合、latin-1を使用（すべてのバイト値を受け入れる）
                    content = content_bytes.decode('latin-1')
                    logger.warning("Falling back to latin-1 encoding")
            else:
                # chardetが利用可能な場合、検出されたエンコーディングを使用
                content = content_bytes.decode(encoding or 'latin-1')
                
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