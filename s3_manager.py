"""Small, testable wrapper around common Amazon S3 object operations."""
from pathlib import Path
from typing import Any
import boto3

class S3FileManager:
    """Manage objects in one S3 bucket using the standard AWS credential chain."""
    def __init__(self, bucket_name: str, client: Any | None = None) -> None:
        if not bucket_name or not bucket_name.strip():
            raise ValueError("bucket_name must not be empty")
        self.bucket_name = bucket_name.strip()
        self.client = client or boto3.client("s3")

    def upload_file(self, file_path: str, object_key: str | None = None) -> str:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {path}")
        key = object_key or path.name
        if not key.strip():
            raise ValueError("object_key must not be empty")
        self.client.upload_file(str(path), self.bucket_name, key)
        return key

    def list_objects(self) -> list[dict[str, Any]]:
        paginator = self.client.get_paginator("list_objects_v2")
        objects: list[dict[str, Any]] = []
        for page in paginator.paginate(Bucket=self.bucket_name):
            objects.extend(page.get("Contents", []))
        return objects

    def generate_download_url(self, object_key: str, expires_in: int = 3600) -> str:
        if not object_key or not object_key.strip():
            raise ValueError("object_key must not be empty")
        if not 1 <= expires_in <= 604800:
            raise ValueError("expires_in must be between 1 and 604800 seconds")
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket_name, "Key": object_key},
            ExpiresIn=expires_in
        )

    def delete_object(self, object_key: str) -> None:
        if not object_key or not object_key.strip():
            raise ValueError("object_key must not be empty")
        self.client.delete_object(Bucket=self.bucket_name, Key=object_key)


def format_size(size_bytes: int) -> str:
    """Format a byte count using readable binary units."""
    if size_bytes < 0:
        raise ValueError("size_bytes must not be negative")
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
