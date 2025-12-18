"""
File Service for managing job description files
Reusable service for any file system operations
"""
import os
import aiofiles
from pathlib import Path
from typing import Optional


class FileService:
    def __init__(self, base_dir: str = "Job descriptions"):
        self.base_dir = base_dir
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Create base directory if it doesn't exist"""
        Path(self.base_dir).mkdir(parents=True, exist_ok=True)
    
    async def save_job_description(self, job_id: str, content: str) -> str:
        """
        Save job description to file system
        
        Args:
            job_id: Unique job identifier
            content: Job description content
            
        Returns:
            Full file path where content was saved
        """
        try:
            file_path = self._get_file_path(job_id)
            
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
                await f.write(content)
            
            return file_path
        except Exception as e:
            raise Exception(f"Failed to save job description: {str(e)}")
    
    async def read_job_description(self, job_id: str) -> Optional[str]:
        """
        Read job description from file system
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Job description content or None if file doesn't exist
        """
        try:
            file_path = self._get_file_path(job_id)
            
            if not os.path.exists(file_path):
                return None
            
            async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
                content = await f.read()
            
            return content
        except Exception as e:
            raise Exception(f"Failed to read job description: {str(e)}")
    
    async def delete_job_description(self, job_id: str) -> bool:
        """
        Delete job description file
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        try:
            file_path = self._get_file_path(job_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            
            return False
        except Exception as e:
            raise Exception(f"Failed to delete job description: {str(e)}")
    
    def _get_file_path(self, job_id: str) -> str:
        """Generate full file path for a job ID"""
        return os.path.join(self.base_dir, f"{job_id}.txt")
    
    def file_exists(self, job_id: str) -> bool:
        """Check if job description file exists"""
        file_path = self._get_file_path(job_id)
        return os.path.exists(file_path)


# Factory function for easy instantiation
def create_file_service() -> FileService:
    """Create and return a configured FileService instance"""
    return FileService()
