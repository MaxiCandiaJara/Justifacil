"""
Custom Django Storage Backend for Supabase Storage using REST API
This version uses direct HTTP requests instead of the supabase-py client
"""
from __future__ import annotations
import os
import requests
from io import BytesIO
from typing import Any
from django.core.files.base import File
from django.core.files.storage import Storage
from django.conf import settings


class SupabaseStorageREST(Storage):
    """
    Custom storage backend for Supabase Storage using REST API.
    Stores files in a Supabase Storage bucket instead of local filesystem.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.supabase_url = getattr(settings, "SUPABASE_URL")
        self.supabase_key = getattr(settings, "SUPABASE_KEY")
        self.bucket_name = getattr(settings, "SUPABASE_BUCKET", "Documentos")
        self.storage_url = f"{self.supabase_url}/storage/v1"

    def _get_headers(self, content_type: str = "application/octet-stream") -> dict:
        """Get headers for Supabase Storage API requests."""
        return {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
            "Content-Type": content_type,
        }

    def _save(self, name: str, content: File) -> str:
        """
        Save file to Supabase Storage bucket using REST API.
        """
        # Normalize path to use forward slashes (Supabase requirement)
        name = name.replace('\\', '/')
        
        content.seek(0)
        file_data = content.read()
        
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        
        url = f"{self.storage_url}/object/{self.bucket_name}/{name}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }
        
        response = requests.post(
            url,
            data=file_data,
            headers=headers
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload file: {response.text}")
        
        return name

    def _open(self, name: str, mode: str = "rb") -> File:
        """
        Retrieve a file from Supabase Storage using REST API.
        """
        # Normalize path to use forward slashes
        name = name.replace('\\', '/')
        
        url = f"{self.storage_url}/object/{self.bucket_name}/{name}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise FileNotFoundError(f"File not found: {name}")
        
        file_obj = BytesIO(response.content)
        file_obj.name = name
        return File(file_obj, name=name)

    def delete(self, name: str) -> None:
        """
        Delete a file from Supabase Storage using REST API.
        """
        # Normalize path to use forward slashes
        name = name.replace('\\', '/')
        
        url = f"{self.storage_url}/object/{self.bucket_name}/{name}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "apikey": self.supabase_key,
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code not in [200, 204]:
            raise Exception(f"Failed to delete file: {response.text}")

    def exists(self, name: str) -> bool:
        """
        Check if a file exists in Supabase Storage using REST API.
        """
        try:
            # Normalize path to use forward slashes
            name = name.replace('\\', '/')
            
            url = f"{self.storage_url}/object/{self.bucket_name}/{name}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "apikey": self.supabase_key,
            }
            
            response = requests.head(url, headers=headers)
            return response.status_code == 200
        except Exception:
            return False

    def url(self, name: str) -> str:
        """
        Get the public URL for a file in Supabase Storage.
        """
        # Normalize path to use forward slashes
        name = name.replace('\\', '/')
        return f"{self.storage_url}/object/public/{self.bucket_name}/{name}"

    def size(self, name: str) -> int:
        """
        Get the size of a file in Supabase Storage.
        """
        try:
            # Normalize path to use forward slashes
            name = name.replace('\\', '/')
            
            url = f"{self.storage_url}/object/{self.bucket_name}/{name}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "apikey": self.supabase_key,
            }
            
            response = requests.head(url, headers=headers)
            if response.status_code == 200:
                return int(response.headers.get('Content-Length', 0))
            return 0
        except Exception:
            return 0

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """
        Get an available filename.
        """
        if self.exists(name):
            import time
            base, ext = os.path.splitext(name)
            name = f"{base}_{int(time.time())}{ext}"
        
        if max_length and len(name) > max_length:
            name = name[:max_length]
            
        return name
