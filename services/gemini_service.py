"""
Gemini API Service
Handles communication with Google Gemini API
"""

from google import genai
from typing import List, Dict
import re

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
    
    def extract_important_words(self, text: str) -> List[str]:
        """
        Extract important words from text using Gemini
        Returns list of words
        """
        preprompt = (
            "Identify words in the following text that are likely useful or important "
            "for an intermediate language learner. List the words separated by commas. "
            "Do not include any explanations—only the words. Text:\n\n"
        )
        
        prompt = f"{preprompt}{text}"
        print("prompt made test len", len(text))
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            print("response received test", response.text[:100])
            # Parse response and split by comma
            words_text = response.text.strip()
            words = [w.strip() for w in words_text.split(',') if w.strip()]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_words = []
            for word in words:
                word_lower = word.lower()
                if word_lower not in seen:
                    seen.add(word_lower)
                    unique_words.append(word)
            
            return unique_words
        except Exception as e:
            print(f"Error extracting words: {e}")
            return []
    
    def get_word_meanings(self, words: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Get meanings and examples for a list of words
        Returns dict: {word: {'meaning': 'Persian meaning', 'examples': 'example sentences'}}
        """
        # preprompt = (
        #     "Each line in the following input contains one English word. "
        #     "For each word, return its Persian meaning and one or more example sentences "
        #     "demonstrating its usage in English. Separate the word, its Persian meaning, "
        #     "and the examples with commas. Separate multiple example sentences with a hyphen (-). "
        #     "Do not add any extra explanation. Words:\n\n"
        # )
        preprompt = (
            "Each line in the following input contains one English word. "
            "For each word, return its Persian meaning(s) and one or more example sentences "
            "demonstrating its usage in English. If the word has multiple meanings, list all "
            "common meanings clearly. Separate the word, its Persian meaning(s), "
            "and the examples with commas. Separate different meanings with a semicolon (;). "
            "Separate multiple example sentences with a hyphen (-). "
            "Do not add any extra explanation. Words:\n\n"
        )
        words_text = '\n'.join(words)
        prompt = f"{preprompt}{words_text}"
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            # Parse response
            meanings_dict = {}
            lines = response.text.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Try to parse: word, meaning, examples
                parts = [p.strip() for p in line.split(',', 2)]
                
                if len(parts) >= 3:
                    word = parts[0]
                    meaning = parts[1]
                    examples = parts[2]
                    
                    meanings_dict[word] = {
                        'meaning': meaning,
                        'examples': examples
                    }
                elif len(parts) == 2:
                    # If no examples provided
                    word = parts[0]
                    meaning = parts[1]
                    meanings_dict[word] = {
                        'meaning': meaning,
                        'examples': ''
                    }
            
            return meanings_dict
        except Exception as e:
            print(f"Error getting meanings: {e}")
            return {}
    
    def get_word_meanings_batch(self, words: List[str], batch_size: int = 50) -> Dict[str, Dict[str, str]]:
        """
        Get meanings for words in batches to handle large lists
        """
        all_meanings = {}
        
        for i in range(0, len(words), batch_size):
            batch = words[i:i + batch_size]
            batch_meanings = self.get_word_meanings(batch)
            all_meanings.update(batch_meanings)
        
        return all_meanings