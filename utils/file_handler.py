"""
File Handler Utility
Helper functions for file operations
"""

import os
import shutil
from typing import Optional

class FileHandler:
    @staticmethod
    def validate_srt_file(file_path: str) -> bool:
        """
        Validate if file exists and is an SRT file
        """
        if not os.path.exists(file_path):
            return False
        
        if not file_path.lower().endswith('.srt'):
            return False
        
        return True
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        Get file size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        Get file size in megabytes
        """
        size_bytes = FileHandler.get_file_size(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    
    @staticmethod
    def copy_file_to_app_data(file_path: str, app_data_dir: str) -> Optional[str]:
        """
        Copy SRT file to application data directory
        Returns new file path or None if failed
        """
        try:
            # Create app data directory if it doesn't exist
            os.makedirs(app_data_dir, exist_ok=True)
            
            # Get filename
            filename = os.path.basename(file_path)
            
            # Create destination path
            dest_path = os.path.join(app_data_dir, filename)
            
            # If file already exists, add number suffix
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(app_data_dir, new_filename)
                counter += 1
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            
            return dest_path
        except Exception as e:
            print(f"Error copying file: {e}")
            return None
    
    @staticmethod
    def read_file_content(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file content as string
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    @staticmethod
    def create_directory(directory_path: str) -> bool:
        """
        Create directory if it doesn't exist
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Convert filename to safe format (remove invalid characters)
        """
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    @staticmethod
    def list_srt_files(directory: str) -> list:
        """
        List all SRT files in a directory
        """
        try:
            if not os.path.exists(directory):
                return []
            
            files = []
            for filename in os.listdir(directory):
                if filename.lower().endswith('.srt'):
                    full_path = os.path.join(directory, filename)
                    files.append(full_path)
            
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []