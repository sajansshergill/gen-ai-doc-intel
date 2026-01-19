"""
Pluggable storage interface (Local, S3, GCS-like).
Clean abstraction for document storage.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path


class StorageBackend(ABC):
    """Abstract storage backend interface."""
    
    @abstractmethod
    def upload(self, file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
        """Upload a file and return its storage key/URL."""
        pass
    
    @abstractmethod
    def download(self, key: str) -> bytes:
        """Download a file by key."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a file exists."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a file by key."""
        pass
    
    @abstractmethod
    def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing the file (with optional expiration)."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def upload(self, file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
        """Upload to local filesystem."""
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(file_obj.read())
        
        return str(file_path.relative_to(self.base_path))
    
    def download(self, key: str) -> bytes:
        """Download from local filesystem."""
        file_path = self.base_path / key
        with open(file_path, "rb") as f:
            return f.read()
    
    def exists(self, key: str) -> bool:
        """Check if file exists."""
        return (self.base_path / key).exists()
    
    def delete(self, key: str) -> bool:
        """Delete file."""
        file_path = self.base_path / key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Return local file path."""
        return str(self.base_path / key)


class S3Storage(StorageBackend):
    """S3-compatible storage backend (for future implementation)."""
    
    def __init__(self, bucket_name: str, endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        # In production, initialize boto3 client here
    
    def upload(self, file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> str:
        """Upload to S3."""
        # TODO: Implement with boto3
        raise NotImplementedError("S3 storage not yet implemented")
    
    def download(self, key: str) -> bytes:
        """Download from S3."""
        raise NotImplementedError("S3 storage not yet implemented")
    
    def exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        raise NotImplementedError("S3 storage not yet implemented")
    
    def delete(self, key: str) -> bool:
        """Delete from S3."""
        raise NotImplementedError("S3 storage not yet implemented")
    
    def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get presigned URL."""
        raise NotImplementedError("S3 storage not yet implemented")
