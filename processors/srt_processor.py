"""
SRT Processor
Handles SRT file processing and text extraction
"""

import re
from typing import List, Set

class SRTProcessor:
    @staticmethod
    def clean_srt(file_path: str) -> List[str]:
        """
        Extract and clean text from SRT file
        Returns list of unique dialogue lines
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # Try with different encoding if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
        
        clean_lines = []
        seen_lines = set()
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip timing lines (format: 00:00:00,000 --> 00:00:00,000)
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3}', line):
                continue
            
            # Skip sequence numbers
            if line.isdigit():
                continue
            
            # Remove HTML tags if present
            line = re.sub(r'<[^>]+>', '', line)
            
            # Skip duplicate lines
            if line not in seen_lines:
                clean_lines.append(line)
                seen_lines.add(line)
        
        return clean_lines
    
    @staticmethod
    def get_text_from_lines(lines: List[str]) -> str:
        """Convert list of lines to single text string"""
        return ' '.join(lines)
    
    @staticmethod
    def filter_known_words(words: List[str], known_words: Set[str]) -> List[str]:
        """
        Filter out known words from the list
        Case-insensitive comparison
        """
        known_words_lower = {w.lower() for w in known_words}
        return [w for w in words if w.lower() not in known_words_lower]