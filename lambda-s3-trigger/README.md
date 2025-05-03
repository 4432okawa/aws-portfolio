# AWS Lambda S3 Trigger Function

This Python Lambda function processes files uploaded to an S3 bucket:
- **Trigger**: Activates on S3 file uploads to `anagram-input-bucket-20250420`.
- **Functionality**: Reads the file, converts text to uppercase, and saves to `anagram-output-bucket-20250420/processed/`.
- **Region**: Configured for `us-west-2`.

## Purpose
Demonstrates proficiency in AWS Lambda, Python, AWS CLI, and security scanning for serverless applications, built with Amazon Q Developer. Showcases ability to automate serverless workflows with secure configurations for cloud engineering roles.

## Files
- `lambda_function.py`: Lambda function code handling S3 events.

## Usage
To deploy and test the Lambda function on Windows, follow these steps:

1. **Install AWS CLI and configure SSO credentials**:
   - Install AWS CLI from `https://aws.amazon.com/cli/`.
   - Configure SSO:
     ```cmd
     aws configure sso
     ```
     - SSO start URL: `https://profile.aws.amazon.com/`
     - SSO region: `us-east-1`
     - Profile name: `my-sso`
   - Verify:
     ```cmd
     aws sts get-caller-identity
     ```

2. **Create input and output S3 buckets**:
   - Create two S3 buckets in `us-west-2` (replace `anagram-input-bucket-20250420` and `anagram-output-bucket-20250420` with globally unique names):
     ```cmd
     aws s3 mb s3://anagram-input-bucket-20250420 --region us-west-2
     aws s3 mb s3://anagram-output-bucket-20250420 --region us-west-2
     ```
   - Verify:
     ```cmd
     aws s3 ls
     ```

3. **Deploy the Lambda function**:
   - Create a ZIP file of `lambda_function.py`:
     - In Windows Explorer, right-click `lambda_function.py` → "Send to" → "Compressed (zipped) folder" to create `lambda_function.zip`.
     - Or use PowerShell:
       ```cmd
       powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda_function.zip"
       ```
   - In AWS Management Console (`https://console.aws.amazon.com/lambda/`):
     - Go to Lambda → "Create function".
     - Set:
       - Function name: `S3TriggerFunction`
       - Runtime: Python 3.9
       - Permissions: Create a new role with basic Lambda permissions.
     - Click "Create function".
     - In "Code" tab, select "Upload from" → ".zip file" → Upload `lambda_function.zip` → "Save".
   - Add an S3 trigger:
     - In "Function overview", click "Add trigger".
     - Select `S3` → Bucket: `anagram-input-bucket-20250420` → Event type: `All object create events` → "Add".
   - Set environment variable (optional, for secure bucket name):
     - Go to "Configuration" → "Environment variables" → "Edit".
     - Add: Key=`OUTPUT_BUCKET`, Value=`anagram-output-bucket-20250420` → "Save".

4. **Configure IAM permissions**:
   - In IAM Console (`https://console.aws.amazon.com/iam/`):
     - Find the Lambda role (e.g., `AWSLambdaBasicExecutionRole-xxxx`).
     - Click "Attach policies" → Search and add `AmazonS3FullAccess` → "Attach policy".
     - For least privilege, create a custom policy:
       ```json
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Action": ["s3:GetObject", "s3:PutObject"],
             "Resource": [
               "arn:aws:s3:::anagram-input-bucket-20250420/*",
               "arn:aws:s3:::anagram-output-bucket-20250420/*"
             ]
           },
           {
             "Effect": "Allow",
             "Action": ["s3:ListBucket"],
             "Resource": [
               "arn:aws:s3:::anagram-input-bucket-20250420",
               "arn:aws:s3:::anagram-output-bucket-20250420"
             ]
           }
         ]
       }
       ```
     - Name: `LambdaS3AccessPolicy` → "Create policy" → Attach to the role.

5. **Test the function**:
   - Create a test file:
     ```cmd
     echo test content > test.txt
     ```
   - Upload to input bucket:
     ```cmd
     aws s3 cp test.txt s3://anagram-input-bucket-20250420/
     ```
   - Verify output:
     ```cmd
     aws s3 ls s3://anagram-output-bucket-20250420/processed/
     ```
     - Expected: `test.txt` with content `TEST CONTENT` (check with `aws s3 cp s3://anagram-output-bucket-20250420/processed/test.txt output.txt` and `type output.txt`).

## Security
- Scanned with Amazon Q Security Scan to ensure no hard-coded credentials.
- Uses `os.environ` to securely retrieve bucket names from environment variables.
- IAM role follows least privilege principle with custom S3 policy.

## Notes
- Replace `anagram-input-bucket-20250420` and `anagram-output-bucket-20250420` with your unique bucket names.
- Ensure Lambda execution role has permissions for S3 and CloudWatch Logs.
- Delete buckets after testing to avoid costs (`aws s3 rb s3://bucket-name --force`).

