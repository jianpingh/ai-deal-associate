import boto3
import os
from botocore.exceptions import NoCredentialsError

def upload_to_s3_and_get_link(file_path: str, object_name: str = None, expiration: int = 3600) -> str:
    """
    Upload a file to an S3 bucket and return a presigned URL.
    
    Args:
        file_path: Absolute path to the file to upload.
        object_name: S3 object name. If not specified, file_name is used.
        expiration: Time in seconds for the presigned URL to remain valid.
    
    Returns:
        Presigned URL as a string, or None if upload failed.
    """
    
    # Retrieve credentials from environment variables
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("AWS_BUCKET_NAME")

    # DEBUG: Check if credentials are loaded (Do not print full keys in production logs)
    print(f"DEBUG: AWS_ACCESS_KEY_ID is {'Set' if aws_access_key else 'Not Set'}")
    print(f"DEBUG: AWS_BUCKET_NAME is {bucket_name}")

    if not aws_access_key or not aws_secret_key or not bucket_name:
        print("Error: AWS credentials or bucket name not set in environment variables.")
        return None
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    region_name = os.getenv("AWS_REGION", "us-east-1")

    if not all([aws_access_key, aws_secret_key, bucket_name]):
        print("Error: AWS credentials or bucket name not set in environment variables.")
        return None

    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region_name
    )

    try:
        # 1. Upload the file
        print(f"Uploading {file_path} to s3://{bucket_name}/{object_name}...")
        s3_client.upload_file(file_path, bucket_name, object_name)
        
        # 2. Generate presigned URL
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response

    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
