"""
SRT Vocabulary Learning Application
Main entry point - With Persian Font Support
"""

import os
# os.environ['KIVY_NO_CONSOLELOG'] = '1'  # Commented to see errors

# IMPORTANT: Register Persian font BEFORE importing Kivy widgets
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# Add fonts directory to resource path
font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
if os.path.exists(font_dir):
    resource_add_path(font_dir)
    print(f"✓ Fonts directory found: {font_dir}")
else:
    print(f"⚠ Fonts directory not found: {font_dir}")

# Register Persian font
try:
    LabelBase.register(
        name='Vazir',
        fn_regular='Vazirmatn-Regular.ttf'
    )
    print("✓ Persian font (Vazir) registered successfully")
except Exception as e:
    print(f"⚠ Warning: Could not register Persian font: {e}")
    print("   Persian text may not display correctly")

# Now import Kivy/KivyMD
from kivymd.app import MDApp
from kivy.lang import Builder
from database.db_manager import DatabaseManager

# Import screens to register them
print("Importing screens...")
try:
    from screens.home_screen import HomeScreen
    print("  ✓ HomeScreen")
except Exception as e:
    print(f"  ✗ HomeScreen: {e}")

try:
    from screens.word_list_screen import WordListScreen
    print("  ✓ WordListScreen")
except Exception as e:
    print(f"  ✗ WordListScreen: {e}")

try:
    from screens.known_words_screen import KnownWordsScreen
    print("  ✓ KnownWordsScreen")
except Exception as e:
    print(f"  ✗ KnownWordsScreen: {e}")

try:
    from screens.srt_library_screen import SRTLibraryScreen
    print("  ✓ SRTLibraryScreen")
except Exception as e:
    print(f"  ✗ SRTLibraryScreen: {e}")

try:
    from screens.settings_screen import SettingsScreen
    print("  ✓ SettingsScreen")
except Exception as e:
    print(f"  ✗ SettingsScreen: {e}")

try:
    from screens.word_viewer_screen import WordViewerScreen
    print("  ✓ WordViewerScreen")
except Exception as e:
    print(f"  ✗ WordViewerScreen: {e}")

# Main KV string for screen manager
KV = '''
MDScreenManager:
    id: screen_manager
    
    HomeScreen:
        name: 'home'
    
    WordListScreen:
        name: 'word_list'
    
    KnownWordsScreen:
        name: 'known_words'
    
    SRTLibraryScreen:
        name: 'srt_library'
    
    SettingsScreen:
        name: 'settings'
    
    WordViewerScreen:
        name: 'word_viewer'
'''

class VocabApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        print("VocabApp initialized")
        
    def build(self):
        print("Building app...")
        # Set theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        print("  ✓ Theme set")
        
        # Initialize database
        db_path = os.path.join(os.path.dirname(__file__), 'vocab.db')
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize_database()
        print("  ✓ Database initialized")
        
        # Build and return the root widget
        print("  Loading KV...")
        root = Builder.load_string(KV)
        print("  ✓ KV loaded")
        return root
    
    def on_stop(self):
        """Called when application stops"""
        print("App stopping...")
        if self.db_manager:
            self.db_manager.close()
        return True

if __name__ == '__main__':
    print("Starting VocabApp...")
    try:
        VocabApp().run()
    except Exception as e:
        print(f"✗ App crashed: {e}")
        import traceback
        traceback.print_exc()