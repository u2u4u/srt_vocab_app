"""
Database Manager
Handles all database operations with thread-safe connections
"""

import sqlite3
from typing import List, Tuple, Optional
import os
import threading

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
        self._connections = []  # Track all connections
        self._lock = threading.Lock()
        
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
            # Track connection with thread safety
            with self._lock:
                self._connections.append(self._local.connection)
        return self._local.connection
    
    def close(self):
        """Close all database connections"""
        # Close current thread's connection
        if hasattr(self._local, 'connection') and self._local.connection:
            try:
                self._local.connection.close()
            except:
                pass
            self._local.connection = None
        
        # Try to close all tracked connections
        with self._lock:
            for conn in self._connections[:]:  # Make a copy to iterate
                try:
                    conn.close()
                except:
                    pass
            self._connections.clear()
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SRT files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS srtfiles (
                id INTEGER NOT NULL UNIQUE,
                srtfile TEXT,
                PRIMARY KEY(id AUTOINCREMENT)
            )
        ''')
        
        # Words table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER NOT NULL UNIQUE,
                word TEXT,
                meaning TEXT,
                srtfile INTEGER,
                PRIMARY KEY(id AUTOINCREMENT),
                FOREIGN KEY(srtfile) REFERENCES srtfiles(id)
            )
        ''')
        
        # Known words table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS known_words (
                id INTEGER NOT NULL UNIQUE,
                word TEXT UNIQUE,
                PRIMARY KEY(id AUTOINCREMENT)
            )
        ''')
        
        conn.commit()
    
    # SRT Files operations
    def add_srt_file(self, filename: str) -> int:
        """Add a new SRT file to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO srtfiles (srtfile) VALUES (?)', (filename,))
        conn.commit()
        return cursor.lastrowid
    
    def get_all_srt_files(self) -> List[Tuple[int, str]]:
        """Get all SRT files"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, srtfile FROM srtfiles ORDER BY id DESC')
        return cursor.fetchall()
    
    def get_srt_file_by_id(self, srt_id: int) -> Optional[Tuple[int, str]]:
        """Get SRT file by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, srtfile FROM srtfiles WHERE id = ?', (srt_id,))
        return cursor.fetchone()
    
    # Words operations
    def add_word(self, word: str, meaning: str, srtfile_id: int) -> int:
        """Add a new word with meaning"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO words (word, meaning, srtfile) VALUES (?, ?, ?)',
            (word, meaning, srtfile_id)
        )
        conn.commit()
        return cursor.lastrowid
    
    def add_words_batch(self, words_data: List[Tuple[str, str, int]]):
        """Add multiple words at once"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            'INSERT INTO words (word, meaning, srtfile) VALUES (?, ?, ?)',
            words_data
        )
        conn.commit()
    
    def get_words_by_srt(self, srtfile_id: int) -> List[dict]:
        """Get all words for a specific SRT file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, word, meaning, srtfile FROM words WHERE srtfile = ? ORDER BY word',
            (srtfile_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_words(self) -> List[dict]:
        """Get all words"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, word, meaning, srtfile FROM words ORDER BY word')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def search_words(self, query: str) -> List[dict]:
        """Search words by partial match"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, word, meaning, srtfile FROM words WHERE word LIKE ? ORDER BY word',
            (f'%{query}%',)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    # Known words operations
    def add_known_word(self, word: str) -> bool:
        """Add a word to known words list"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO known_words (word) VALUES (?)', (word.lower(),))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Word already exists
    
    def remove_known_word(self, word: str):
        """Remove a word from known words list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM known_words WHERE word = ?', (word.lower(),))
        conn.commit()
    
    def get_all_known_words(self) -> List[str]:
        """Get all known words"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM known_words ORDER BY word')
        return [row[0] for row in cursor.fetchall()]
    
    def is_word_known(self, word: str) -> bool:
        """Check if a word is in known words list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM known_words WHERE word = ?', (word.lower(),))
        return cursor.fetchone()[0] > 0