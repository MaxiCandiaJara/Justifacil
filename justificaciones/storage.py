"""
Custom Django Storage Backend for Supabase Storage
"""
from __future__ import annotations
import os
from io import BytesIO
from typing import Any
from django.core.files.base import File
from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client, Client


class SupabaseStorage(Storage):
    """
    Custom storage backend for Supabase Storage.
    Stores files in a Supabase Storage bucket instead of local filesystem.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.supabase_url = getattr(settings, "SUPABASE_URL")
        self.supabase_key = getattr(settings, "SUPABASE_KEY")
        self.bucket_name = getattr(settings, "SUPABASE_BUCKET", "Documentos")
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Lazy initialization of Supabase client."""
        if self._client is None:
            self._client = create_client(self.supabase_url, self.supabase_key)
        return self._client


    def _save(self, name: str, content: File) -> str:
        """
        Save file to Supabase Storage bucket.
        
        Args:
            name: The name/path of the file to save
            content: The file content to upload
            
        Returns:
            The name/path of the saved file
        """
        # Read file content
        content.seek(0)
        file_data = content.read()
        
        # Upload to Supabase Storage
        self.client.storage.from_(self.bucket_name).upload(
            path=name,
            file=file_data,
            file_options={"content-type": content.content_type if hasattr(content, 'content_type') else "application/octet-stream"}
        )
        
        return name

    def _open(self, name: str, mode: str = "rb") -> File:
        """
        Retrieve a file from Supabase Storage.
        
        Args:
            name: The name/path of the file to open
            mode: The file mode (only 'rb' is supported)
            
        Returns:
            A File object containing the file data
        """
        # Download file from Supabase
        response = self.client.storage.from_(self.bucket_name).download(name)
        
        # Create a File object from the bytes
        file_obj = BytesIO(response)
        file_obj.name = name
        return File(file_obj, name=name)

    def delete(self, name: str) -> None:
        """
        Delete a file from Supabase Storage.
        
        Args:
            name: The name/path of the file to delete
        """
        self.client.storage.from_(self.bucket_name).remove([name])

    def exists(self, name: str) -> bool:
        """
        Check if a file exists in Supabase Storage.
        
        Args:
            name: The name/path of the file to check
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            # List files in the bucket and check if our file is there
            files = self.client.storage.from_(self.bucket_name).list()
            # Extract just the filename from the path
            filename = os.path.basename(name)
            return any(f.get("name") == filename for f in files)
        except Exception:
            return False

    def url(self, name: str) -> str:
        """
        Get the public URL for a file in Supabase Storage.
        
        Args:
            name: The name/path of the file
            
        Returns:
            The public URL to access the file
        """
        # Get public URL from Supabase
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(name)
        return public_url

    def size(self, name: str) -> int:
        """
        Get the size of a file in Supabase Storage.
        
        Args:
            name: The name/path of the file
            
        Returns:
            The size of the file in bytes
        """
        try:
            # Download the file to get its size
            response = self.client.storage.from_(self.bucket_name).download(name)
            return len(response)
        except Exception:
            return 0

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """
        Get an available filename. If a file with the given name already exists,
        append a suffix to make it unique.
        
        Args:
            name: The desired filename
            max_length: Maximum length for the filename
            
        Returns:
            An available filename
        """
        if self.exists(name):
            # If file exists, append a timestamp or counter
            import time
            base, ext = os.path.splitext(name)
            name = f"{base}_{int(time.time())}{ext}"
        
        if max_length and len(name) > max_length:
            name = name[:max_length]
            
        return name
