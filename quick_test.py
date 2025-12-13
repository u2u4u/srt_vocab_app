"""
Quick Test Script
Test database operations in multiple threads
"""

import threading
import time
from database.db_manager import DatabaseManager

def test_thread(db, thread_id):
    """Test database operations in a thread"""
    print(f"Thread {thread_id} starting...")
    
    try:
        # Add known word
        word = f"test_word_{thread_id}"
        result = db.add_known_word(word)
        print(f"Thread {thread_id}: Added word '{word}' - {result}")
        
        # Get all known words
        words = db.get_all_known_words()
        print(f"Thread {thread_id}: Found {len(words)} known words")
        
        # Add SRT file
        srt_id = db.add_srt_file(f"test_{thread_id}.srt")
        print(f"Thread {thread_id}: Added SRT file with ID {srt_id}")
        
        # Add words to database
        words_data = [
            (f"word1_{thread_id}", "meaning1", srt_id),
            (f"word2_{thread_id}", "meaning2", srt_id),
        ]
        db.add_words_batch(words_data)
        print(f"Thread {thread_id}: Added batch of words")
        
        # Get words for SRT
        words = db.get_words_by_srt(srt_id)
        print(f"Thread {thread_id}: Retrieved {len(words)} words for SRT {srt_id}")
        
        print(f"Thread {thread_id}: ✓ All operations successful")
        
    except Exception as e:
        print(f"Thread {thread_id}: ✗ Error: {e}")

def main():
    """Run multi-threaded test"""
    print("=" * 60)
    print("Database Thread Safety Test")
    print("=" * 60)
    print()
    
    # Create database manager
    db = DatabaseManager("test_threading.db")
    db.initialize_database()
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=test_thread, args=(db, i))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    # Close all connections before cleanup
    db.close()
    time.sleep(0.5)  # Give OS time to release file handles
    
    # Cleanup
    import os
    try:
        if os.path.exists("test_threading.db"):
            os.remove("test_threading.db")
            print("Test database cleaned up.")
    except PermissionError:
        print("Note: Could not delete test database (file still in use).")
        print("You can safely delete 'test_threading.db' manually.")

if __name__ == '__main__':
    main()