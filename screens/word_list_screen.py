"""
Word List Screen - Optimized Version
Display and manage extracted words before fetching meanings
Uses RecycleView for better performance with large lists
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from services.gemini_service import GeminiService
import threading

Builder.load_string('''
<SelectableWordItem>:
    size_hint_y: None
    height: dp(72)
    
    MDCard:
        orientation: 'horizontal'
        padding: [dp(16), dp(8)]
        elevation: 1
        ripple_behavior: True
        on_release: root.mark_known()
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(16)
            
            MDIcon:
                icon: "text"
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(4)
                
                MDLabel:
                    text: root.word_text
                    font_style: "Body1"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    text: "Tap to mark as known"
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: self.texture_size[1]
            
            MDIcon:
                icon: "close-circle-outline"
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}

<WordListScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Review Words"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            
            MDCard:
                size_hint_y: None
                height: dp(60)
                padding: dp(10)
                elevation: 2
                
                MDBoxLayout:
                    orientation: 'vertical'
                    
                    MDLabel:
                        text: root.info_text
                        font_style: "Body2"
                        halign: "center"
            
            RecycleView:
                id: words_recycler
                viewclass: 'SelectableWordItem'
                
                RecycleBoxLayout:
                    default_size: None, dp(72)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    spacing: dp(2)
            
            MDRaisedButton:
                text: "Fetch Meanings"
                size_hint_y: None
                height: dp(50)
                pos_hint: {'center_x': 0.5}
                on_release: root.fetch_meanings()
''')

class SelectableWordItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable word item for efficient list rendering"""
    word_text = StringProperty()
    index = None
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when the view is being recycled"""
        self.index = index
        self.word_text = data['word']
        return super().refresh_view_attrs(rv, index, data)
    
    def mark_known(self):
        """Mark this word as known"""
        screen = self.get_root_window().children[0].current_screen
        if hasattr(screen, 'mark_word_as_known'):
            screen.mark_word_as_known(self.word_text, self.index)

class WordListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.srt_id = None
        self.words = []
        self.progress_dialog = None
    
    @property
    def info_text(self):
        count = len(self.words)
        return f"{count} words to review - Tap to mark as known"
    
    def set_words(self, srt_id, words):
        """Set words to display"""
        self.srt_id = srt_id
        self.words = words
        self.populate_word_list()
    
    def populate_word_list(self):
        """Populate the RecycleView with words"""
        # Convert words to data format for RecycleView
        self.ids.words_recycler.data = [
            {'word': word} for word in self.words
        ]
    
    def mark_word_as_known(self, word, index):
        """Mark word as known and remove from list"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        # Add to known words
        if db.add_known_word(word):
            # Remove from list
            if word in self.words:
                self.words.remove(word)
                # Update RecycleView data
                Clock.schedule_once(lambda dt: self.populate_word_list(), 0)
    
    def fetch_meanings(self):
        """Fetch meanings for all words"""
        if not self.words:
            self.show_dialog("No Words", "No words to fetch meanings for.")
            return
        
        self.show_progress_dialog(f"Fetching meanings for {len(self.words)} words...")
        
        # Process in background
        threading.Thread(
            target=self.process_meanings,
            daemon=True
        ).start()
    
    def process_meanings(self):
        """Process and save word meanings"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            db = app.db_manager
            
            # Get meanings from Gemini
            gemini = GeminiService("AIzaSyBr2gHO058kDWxBuK6_v9tySIZqsUbY81E")
            meanings_dict = gemini.get_word_meanings_batch(self.words)
            
            # Save to database
            words_data = []
            for word in self.words:
                if word in meanings_dict:
                    meaning_text = meanings_dict[word]['meaning']
                    examples_text = meanings_dict[word]['examples']
                    full_meaning = f"{meaning_text} | Examples: {examples_text}"
                    words_data.append((word, full_meaning, self.srt_id))
                else:
                    words_data.append((word, "Meaning not found", self.srt_id))
            
            db.add_words_batch(words_data)
            
            # Navigate back to home
            Clock.schedule_once(lambda dt: self.finish_processing(), 0)
            
        except Exception as e:
            print(f"Error processing meanings: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self.close_progress_dialog(), 0)
    
    def finish_processing(self):
        """Finish processing and navigate"""
        self.close_progress_dialog()
        self.show_dialog(
            "Success",
            "Words and meanings saved successfully!",
            on_dismiss=lambda x: self.go_to_library()
        )
    
    def go_to_library(self):
        """Navigate to library"""
        self.manager.current = 'srt_library'
    
    def show_progress_dialog(self, text):
        """Show loading dialog"""
        self.progress_dialog = MDDialog(
            text=text,
            auto_dismiss=False
        )
        self.progress_dialog.open()
    
    def close_progress_dialog(self):
        """Close loading dialog"""
        if self.progress_dialog:
            self.progress_dialog.dismiss()
            self.progress_dialog = None
    
    def show_dialog(self, title, text, on_dismiss=None):
        """Show info dialog"""
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        if on_dismiss:
            dialog.bind(on_dismiss=on_dismiss)
        dialog.open()
    
    def go_back(self):
        """Go back to home"""
        self.manager.current = 'home'