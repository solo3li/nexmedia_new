import os
import boto3
from botocore.client import Config
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MinioStorageService:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.public_endpoint = settings.MINIO_PUBLIC_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME

        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            buckets = [b['Name'] for b in self.s3_client.list_buckets().get('Buckets', [])]
            if self.bucket_name not in buckets:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} created in MinIO.")
        except Exception as e:
            logger.warning(f"Could not connect to MinIO during startup: {e}")

    def upload_file_bytes(self, file_bytes: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        """Upload raw bytes to MinIO and return internal object path."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_bytes,
                ContentType=content_type
            )
            return object_name
        except Exception as e:
            logger.error(f"Failed to upload bytes to MinIO: {e}")
            raise

    def get_presigned_url(self, object_name: str, expires_in: int = 86400) -> str:
        """Generate a presigned GET URL for public downloading."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expires_in
            )
            # Replace internal docker endpoint with public client-accessible endpoint
            if self.endpoint != self.public_endpoint:
                url = url.replace(self.endpoint, self.public_endpoint)
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL for {object_name}: {e}")
            return f"{self.public_endpoint}/{self.bucket_name}/{object_name}"

storage_service = MinioStorageService()
