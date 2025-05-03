# Lambda function to process S3 file uploads and convert text to uppercase
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {key} from bucket: {bucket}")

        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        upper_content = content.upper()

        output_bucket = os.environ.get('OUTPUT_BUCKET', 'anagram-output-bucket-20250420')
        output_key = f"processed/{key}"
        s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=upper_content)

        logger.info(f"Saved to {output_bucket}/{output_key}")
        return {
            'statusCode': 200,
            'body': json.dumps('File processed successfully')
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise e