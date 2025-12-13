"""
Word Viewer Screen - Complete Fixed Version
View words and meanings from a specific SRT file
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty

Builder.load_string('''
<WordViewItem>:
    size_hint_y: None
    height: dp(140)
    
    MDCard:
        orientation: 'vertical'
        padding: [dp(10), dp(8), dp(10), dp(8)]
        spacing: dp(4)
        elevation: 2
        radius: [dp(6)]
        
        # Header: Word + Button
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(36)
            spacing: dp(8)
            
            MDLabel:
                text: root.word_text
                font_style: "H6"
                bold: True
                size_hint_x: 0.6
                valign: "center"
                padding: [dp(2), 0]
            
            Widget:
                size_hint_x: 0.1
            
            MDRaisedButton:
                text: "✓"
                size_hint: None, None
                size: dp(80), dp(32)
                font_size: "14sp"
                on_release: root.mark_learned()
        
        MDSeparator:
            height: dp(1)
        
        # Persian Meaning - Right aligned with Vazir font
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(50)
            padding: [dp(2), dp(4)]
            
            MDLabel:
                text: root.meaning_text
                font_name: "Vazir"
                halign: "right"
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]
        
        # Examples
        MDLabel:
            text: root.examples_text
            font_style: "Caption"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(30) if self.text else dp(1)
            padding: [dp(2), 0]
            text_size: self.width, None

<WordViewerScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            id: topbar
            title: "Words"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        
        RecycleView:
            id: words_recycler
            viewclass: 'WordViewItem'
            
            RecycleBoxLayout:
                default_size: None, dp(140)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(8)
                padding: dp(10)
''')

class WordViewItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable word view item"""
    word_text = StringProperty()
    meaning_text = StringProperty()
    examples_text = StringProperty()
    index = None
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when the view is being recycled"""
        self.index = index
        self.word_text = data['word']
        self.meaning_text = data['meaning']
        self.examples_text = data['examples']
        return super().refresh_view_attrs(rv, index, data)
    
    def mark_learned(self):
        """Mark word as learned"""
        from kivymd.app import MDApp
        
        # Get the app and call mark_word_learned directly
        app = MDApp.get_running_app()
        if app and hasattr(app.root, 'current_screen'):
            current_screen = app.root.current_screen
            if hasattr(current_screen, 'mark_word_learned'):
                current_screen.mark_word_learned(self.word_text)
                return
        
        # Fallback: Direct database access
        try:
            db = app.db_manager
            if db.add_known_word(self.word_text):
                from kivymd.toast import toast
                toast(f"'{self.word_text}' added!")
            else:
                from kivymd.toast import toast
                toast(f"Already known")
        except Exception as e:
            print(f"Error marking word as learned: {e}")

class WordViewerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.srt_id = None
        self.srt_name = ""
    
    def set_words(self, srt_id, srt_name, words_data):
        """Set words to display"""
        from utils.persian_text_helper import fix_persian_text
        from kivymd.app import MDApp
        
        app = MDApp.get_running_app()
        db = app.db_manager
        
        self.srt_id = srt_id
        self.srt_name = srt_name
        
        # Get known words to filter them out
        known_words = set(db.get_all_known_words())
        
        # Prepare data for RecycleView
        recycler_data = []
        for word_data in words_data:
            word = word_data['word']
            
            # Skip if already known
            if word.lower() in known_words:
                continue
            
            meaning = word_data['meaning']
            
            # Parse meaning
            if '|' in meaning:
                parts = meaning.split('|', 1)
                persian_meaning = parts[0].strip()
                examples = parts[1].replace('Examples:', '').strip()
                
                # Fix Persian text for RTL display
                persian_meaning = fix_persian_text(persian_meaning)
                
                # Truncate if too long
                if len(examples) > 100:
                    examples = examples[:100] + "..."
                examples_display = f"Ex: {examples}" if examples else ""
            else:
                persian_meaning = meaning[:100] + "..." if len(meaning) > 100 else meaning
                # Fix Persian text
                persian_meaning = fix_persian_text(persian_meaning)
                examples_display = ""
            
            recycler_data.append({
                'word': word,
                'meaning': persian_meaning,
                'examples': examples_display
            })
        
        # Update title with filtered count
        self.ids.topbar.title = f"{srt_name} ({len(recycler_data)} words)"
        self.ids.words_recycler.data = recycler_data
    
    def remove_word_from_list(self, word):
        """Remove a word from the displayed list"""
        # Get current data
        current_data = self.ids.words_recycler.data
        
        # Filter out the word
        new_data = [item for item in current_data if item['word'] != word]
        
        # Update RecycleView
        self.ids.words_recycler.data = new_data
        
        # Update title
        self.ids.topbar.title = f"{self.srt_name} ({len(new_data)} words)"
    
    def mark_word_learned(self, word):
        """Mark word as learned"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        if db.add_known_word(word):
            from kivymd.toast import toast
            toast(f"'{word}' added!")
            
            # Remove from list after marking as learned
            Clock.schedule_once(lambda dt: self.remove_word_from_list(word), 0.1)
        else:
            from kivymd.toast import toast
            toast(f"Already known")
            
            # Still remove from list even if already known
            Clock.schedule_once(lambda dt: self.remove_word_from_list(word), 0.1)
    
    def go_back(self):
        """Go back to library"""
        self.manager.current = 'srt_library'