import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
import os
import shutil
import logging
from app.core.config import settings

logger = logging.getLogger("s3_service")

class S3Service:
    def __init__(self):
        self.use_s3 = bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
        if self.use_s3:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}. Falling back to local storage.")
                self.use_s3 = False

        if not self.use_s3:
            # Set up local storage folders
            self.local_dir = os.path.join(os.getcwd(), "local_storage")
            os.makedirs(self.local_dir, exist_ok=True)
            logger.info(f"Using local filesystem fallback storage at {self.local_dir}")

    async def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """
        Uploads file to S3 (or local path fallback) and returns a unique key or path.
        """
        if self.use_s3:
            try:
                self.s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=file_name,
                    Body=file_content,
                    ContentType=content_type
                )
                return file_name
            except ClientError as e:
                logger.error(f"S3 upload failed: {e}")
                raise RuntimeError(f"Storage upload failed: {str(e)}")
        else:
            # Save file locally
            file_path = os.path.join(self.local_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_content)
            return file_name

    async def get_presigned_url(self, file_key: str, expiration_seconds: int = 3600) -> str:
        """
        Generates a pre-signed S3 URL, or returns a local file-server URL.
        """
        if self.use_s3:
            try:
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": settings.S3_BUCKET_NAME, "Key": file_key},
                    ExpiresIn=expiration_seconds
                )
                return url
            except ClientError as e:
                logger.error(f"S3 pre-signed URL generation failed: {e}")
                raise RuntimeError(f"Storage URL generation failed: {str(e)}")
        else:
            # Return relative or absolute URL targeting the local static server
            # Assuming backend uvicorn server runs at http://localhost:8000
            return f"/api/v1/resume/download/local/{file_key}"

s3_service = S3Service()
