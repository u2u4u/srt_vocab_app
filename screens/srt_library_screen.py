"""
SRT Library Screen - Complete with Delete and Recheck Functions
View all SRT files and their associated words with RecycleView
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty
from services.gemini_service import GeminiService
from utils.settings_manager import get_settings_manager
import threading

Builder.load_string('''
<SRTFileItem>:
    size_hint_y: None
    height: dp(72)
    
    MDCard:
        orientation: 'horizontal'
        padding: [dp(12), dp(8)]
        elevation: 1
        spacing: dp(8)
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(12)
            
            MDIcon:
                icon: "file-document"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(4)
                on_touch_down: root.on_card_touch(args[1])
                
                MDLabel:
                    text: root.file_name
                    font_style: "Body1"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    text: "Tap to view words"
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: self.texture_size[1]
            
            MDIcon:
                icon: "chevron-right"
                size_hint: None, None
                size: dp(32), dp(32)
                pos_hint: {'center_y': 0.5}
        
        Widget:
            size_hint_x: None
            width: dp(4)
        
        MDIconButton:
            icon: "export"
            theme_text_color: "Custom"
            text_color: 0, 0.7, 0, 1
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {'center_y': 0.5}
            on_release: root.export_words()
        
        MDIconButton:
            icon: "refresh"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {'center_y': 0.5}
            on_release: root.recheck_meanings()
        
        MDIconButton:
            icon: "delete"
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {'center_y': 0.5}
            on_release: root.delete_srt()

<SRTLibraryScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "SRT Library"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        
        RecycleView:
            id: srt_recycler
            viewclass: 'SRTFileItem'
            
            RecycleBoxLayout:
                default_size: None, dp(72)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(8)
                padding: dp(10)
''')

class SRTFileItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable SRT file item"""
    file_name = StringProperty()
    srt_id = 0
    index = None
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when the view is being recycled"""
        self.index = index
        self.file_name = data['file_name']
        self.srt_id = data['srt_id']
        return super().refresh_view_attrs(rv, index, data)
    
    def on_card_touch(self, touch):
        """Handle touch on the card area"""
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                return False
            self.show_words()
            return True
        return False
    
    def show_words(self):
        """Show words for this SRT file"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        screen = app.root.current_screen
        if hasattr(screen, 'show_words_for_srt'):
            screen.show_words_for_srt(self.srt_id, self.file_name)
    
    def delete_srt(self):
        """Delete this SRT file"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        screen = app.root.current_screen
        if hasattr(screen, 'confirm_delete_srt'):
            screen.confirm_delete_srt(self.srt_id, self.file_name)
    
    def recheck_meanings(self):
        """Recheck meanings for words in this SRT"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        screen = app.root.current_screen
        if hasattr(screen, 'recheck_srt_meanings'):
            screen.recheck_srt_meanings(self.srt_id, self.file_name)
    
    def export_words(self):
        """Export words to file"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        screen = app.root.current_screen
        if hasattr(screen, 'export_srt_words'):
            screen.export_srt_words(self.srt_id, self.file_name)

class SRTLibraryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_dialog = None
        self.progress_dialog = None
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_srt_files()
    
    def load_srt_files(self):
        """Load all SRT files from database"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        srt_files = db.get_all_srt_files()
        self.populate_srt_list(srt_files)
    
    def populate_srt_list(self, srt_files):
        """Populate list with SRT files"""
        self.ids.srt_recycler.data = [
            {
                'file_name': srt_name,
                'srt_id': srt_id
            }
            for srt_id, srt_name in srt_files
        ]
    
    def show_words_for_srt(self, srt_id, srt_name):
        """Navigate to word viewer screen"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        # Get words from database
        words_data = db.get_words_by_srt(srt_id)
        
        if not words_data:
            self.show_dialog("No Words", f"No words found for {srt_name}")
            return
        
        # Navigate to word viewer screen
        viewer_screen = self.manager.get_screen('word_viewer')
        viewer_screen.set_words(srt_id, srt_name, words_data)
        self.manager.current = 'word_viewer'
    
    def confirm_delete_srt(self, srt_id, srt_name):
        """Show confirmation dialog before deleting SRT"""
        dialog = MDDialog(
            title="Delete SRT File",
            text=f"Delete '{srt_name}' and all its words?\n\nThis cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=(1, 0, 0, 1),
                    on_release=lambda x: self.delete_srt_file(srt_id, srt_name, dialog)
                ),
            ],
        )
        dialog.open()
    
    def delete_srt_file(self, srt_id, srt_name, dialog):
        """Delete SRT file and all associated words"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        try:
            # Delete all words for this SRT
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM words WHERE srtfile = ?', (srt_id,))
            
            # Delete the SRT file record
            cursor.execute('DELETE FROM srtfiles WHERE id = ?', (srt_id,))
            
            conn.commit()
            
            # Close dialog
            dialog.dismiss()
            
            # Show success message
            self.show_toast(f"'{srt_name}' deleted")
            
            # Reload the list
            Clock.schedule_once(lambda dt: self.load_srt_files(), 0.1)
            
        except Exception as e:
            print(f"Error deleting SRT: {e}")
            self.show_toast("Error deleting file")
    
    def recheck_srt_meanings(self, srt_id, srt_name):
        """Recheck and update meanings for words without meanings"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        # Get all words for this SRT
        words_data = db.get_words_by_srt(srt_id)
        
        if not words_data:
            self.show_toast("No words found in this SRT")
            return
        
        # Find words without meanings or with "Meaning not found"
        words_to_update = []
        for word_data in words_data:
            meaning = word_data['meaning']
            if not meaning or meaning.strip() == "" or meaning.strip().lower() == "meaning not found":
                words_to_update.append(word_data['word'])
        
        if not words_to_update:
            self.show_dialog(
                "All Set!",
                f"All words in '{srt_name}' already have meanings."
            )
            return
        
        # Show confirmation dialog
        dialog = MDDialog(
            title="Recheck Meanings",
            text=f"Found {len(words_to_update)} word(s) without meanings in '{srt_name}'.\n\nFetch meanings now?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="FETCH",
                    on_release=lambda x: self.start_recheck_process(srt_id, words_to_update, dialog)
                ),
            ],
        )
        dialog.open()
    
    def start_recheck_process(self, srt_id, words_to_update, confirm_dialog):
        """Start the recheck process in background"""
        confirm_dialog.dismiss()
        
        self.show_progress_dialog(f"Fetching meanings for {len(words_to_update)} words...")
        
        # Process in background thread
        threading.Thread(
            target=self.process_recheck_meanings,
            args=(srt_id, words_to_update),
            daemon=True
        ).start()
    
    def process_recheck_meanings(self, srt_id, words_to_update):
        """Process and update word meanings in background"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            db = app.db_manager
            
            # Get settings for API key and translation language
            settings = get_settings_manager()
            api_key = settings.get_next_api_key()
            
            if not api_key:
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog("No API key configured"),
                    0
                )
                Clock.schedule_once(lambda dt: self.close_progress_dialog(), 0)
                return
            
            translate_lang = settings.get_translate_language()
            
            # Get meanings from Gemini
            gemini = GeminiService(api_key)
            meanings_dict = gemini.get_word_meanings_batch(words_to_update)
            
            # Update database
            conn = db.get_connection()
            cursor = conn.cursor()
            
            updated_count = 0
            for word in words_to_update:
                if word in meanings_dict:
                    meaning_text = meanings_dict[word]['meaning']
                    examples_text = meanings_dict[word]['examples']
                    full_meaning = f"{meaning_text} | Examples: {examples_text}"
                    
                    # Update the word meaning
                    cursor.execute(
                        'UPDATE words SET meaning = ? WHERE word = ? AND srtfile = ?',
                        (full_meaning, word, srt_id)
                    )
                    updated_count += 1
            
            conn.commit()
            
            # Show success message
            Clock.schedule_once(
                lambda dt: self.finish_recheck_process(updated_count),
                0
            )
            
        except Exception as e:
            print(f"Error rechecking meanings: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(
                lambda dt: self.show_error_dialog(f"Error: {str(e)}"),
                0
            )
            Clock.schedule_once(lambda dt: self.close_progress_dialog(), 0)
    
    def finish_recheck_process(self, updated_count):
        """Finish recheck process and show result"""
        self.close_progress_dialog()
        self.show_dialog(
            "Success",
            f"Updated meanings for {updated_count} word(s)!"
        )
    
    def export_srt_words(self, srt_id, srt_name):
        """Export words to text file in tab-separated format"""
        from kivymd.app import MDApp
        import os
        
        app = MDApp.get_running_app()
        db = app.db_manager
        
        # Get all words for this SRT
        words_data = db.get_words_by_srt(srt_id)
        
        if not words_data:
            self.show_toast("No words to export")
            return
        
        try:
            # Create export filename
            safe_name = srt_name.replace('.srt', '').replace(' ', '_')
            export_filename = f"{safe_name}_words.txt"
            export_path = os.path.join(os.path.dirname(__file__), '..', export_filename)
            
            # Write to file in tab-separated format
            with open(export_path, 'w', encoding='utf-8') as f:
                for word_data in words_data:
                    word = word_data['word']
                    meaning = word_data['meaning']
                    
                    # Write word and meaning separated by tab
                    f.write(f"{word}\t{meaning}\n")
            
            self.show_dialog(
                "Export Successful",
                f"Exported {len(words_data)} words to:\n{export_filename}"
            )
            
        except Exception as e:
            print(f"Error exporting words: {e}")
            self.show_error_dialog(f"Export failed: {str(e)}")
    
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
    
    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_toast(self, message):
        """Show a quick toast message"""
        from kivymd.toast import toast
        toast(message)
    
    def show_dialog(self, title, text):
        """Show simple dialog"""
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
        dialog.open()
    
    def go_back(self):
        """Go back to home"""
        self.manager.current = 'home'