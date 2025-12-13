"""
Settings Manager
Handles application settings including API keys
Stores settings in JSON format with rotation support
"""

import json
import os
from typing import List, Optional
import threading

class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings = {}
        self._lock = threading.Lock()
        self._current_key_index = 0
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self._default_settings()
        else:
            self.settings = self._default_settings()
            self.save_settings()
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _default_settings(self) -> dict:
        """Return default settings structure"""
        return {
            "api_keys": [],
            "theme": "Light",
            "language": "en"
        }
    
    # API Keys Management
    
    def get_api_keys(self) -> List[str]:
        """Get all API keys"""
        return self.settings.get("api_keys", [])
    
    def add_api_key(self, api_key: str) -> bool:
        """
        Add a new API key
        Returns True if added successfully
        """
        if not api_key or not api_key.strip():
            return False
        
        api_key = api_key.strip()
        
        # Check if already exists
        if api_key in self.settings.get("api_keys", []):
            return False
        
        with self._lock:
            if "api_keys" not in self.settings:
                self.settings["api_keys"] = []
            
            self.settings["api_keys"].append(api_key)
            return self.save_settings()
    
    def remove_api_key(self, api_key: str) -> bool:
        """
        Remove an API key
        Returns True if removed successfully
        """
        with self._lock:
            if "api_keys" in self.settings and api_key in self.settings["api_keys"]:
                self.settings["api_keys"].remove(api_key)
                
                # Reset index if needed
                if self._current_key_index >= len(self.settings["api_keys"]):
                    self._current_key_index = 0
                
                return self.save_settings()
        return False
    
    def get_next_api_key(self) -> Optional[str]:
        with self._lock:
            api_keys = self.settings.get("api_keys", [])
            
            if not api_keys:
                return None
            
            # Get current key
            key = api_keys[self._current_key_index]
            
            # Move to next key for next call
            self._current_key_index = (self._current_key_index + 1) % len(api_keys)
            
            return key
    
    def get_api_key_count(self) -> int:
        """Get number of API keys"""
        return len(self.settings.get("api_keys", []))
    
    def has_api_keys(self) -> bool:
        """Check if any API keys are configured"""
        return self.get_api_key_count() > 0
    
    # Theme Management
    
    def get_theme(self) -> str:
        """Get current theme (Light/Dark)"""
        return self.settings.get("theme", "Light")
    
    def set_theme(self, theme: str) -> bool:
        """Set theme (Light/Dark)"""
        if theme in ["Light", "Dark"]:
            self.settings["theme"] = theme
            return self.save_settings()
        return False
    
    # Language Management
    
    def get_language(self) -> str:
        """Get current language"""
        return self.settings.get("language", "en")
    
    def set_language(self, language: str) -> bool:
        """Set language"""
        self.settings["language"] = language
        return self.save_settings()


# Singleton instance
_settings_manager_instance = None

def get_settings_manager(settings_file: str = "settings.json") -> SettingsManager:
    """
    Get singleton instance of SettingsManager
    
    Usage:
        from utils.settings_manager import get_settings_manager
        
        settings = get_settings_manager()
        api_key = settings.get_next_api_key()
    """
    global _settings_manager_instance
    if _settings_manager_instance is None:
        _settings_manager_instance = SettingsManager(settings_file)
    return _settings_manager_instance