"""
Home Screen - Fixed Version
Main navigation screen
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.metrics import dp
from processors.srt_processor import SRTProcessor
from services.gemini_service import GeminiService
import os
import threading
from kivy.clock import Clock
from utils.settings_manager import get_settings_manager

Builder.load_string('''
<HomeScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)
        
        MDTopAppBar:
            title: "SRT Vocabulary Extractor"
            elevation: 2
            right_action_items: [["cog", lambda x: root.open_settings()]]
        
        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(10)
                adaptive_height: True
                
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(15)
                    size_hint_y: None
                    height: dp(200)
                    elevation: 3
                    
                    MDLabel:
                        text: "Upload SRT File"
                        font_style: "H6"
                        halign: "center"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDLabel:
                        text: "Extract vocabulary from subtitle files"
                        font_style: "Body2"
                        halign: "center"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDRaisedButton:
                        text: "Choose SRT File"
                        pos_hint: {'center_x': 0.5}
                        size_hint_x: 0.6
                        on_release: root.choose_file()
                
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(15)
                    size_hint_y: None
                    height: dp(150)
                    elevation: 3
                    
                    MDLabel:
                        text: "View SRT Library"
                        font_style: "H6"
                        halign: "center"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDRaisedButton:
                        text: "Open Library"
                        pos_hint: {'center_x': 0.5}
                        size_hint_x: 0.6
                        on_release: root.open_library()
                
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(15)
                    size_hint_y: None
                    height: dp(150)
                    elevation: 3
                    
                    MDLabel:
                        text: "Manage Known Words"
                        font_style: "H6"
                        halign: "center"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDRaisedButton:
                        text: "Open Known Words"
                        pos_hint: {'center_x': 0.5}
                        size_hint_x: 0.6
                        on_release: root.open_known_words()
''')

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_chooser_dialog = None
        self.progress_dialog = None
    
    def choose_file(self):
        """Open file chooser using platform file dialog"""
        try:
            from plyer import filechooser
            path = filechooser.open_file(
                title="Select SRT File",
                filters=[("SRT Files", "*.srt")]
            )
            if path:
                self.process_selected_file(path[0])
        except ImportError:
            # Fallback to simple input if plyer not available
            self.show_simple_file_dialog()
    
    def show_simple_file_dialog(self):
        """Simple file path input dialog"""
        from kivymd.uix.textfield import MDTextField
        
        content = MDTextField(
            hint_text="Enter full path to SRT file",
            size_hint_x=None,
            width=dp(300)
        )
        
        dialog = MDDialog(
            title="Select SRT File",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SELECT",
                    on_release=lambda x: self.process_path_input(content.text, dialog)
                ),
            ],
        )
        dialog.open()
    
    def process_path_input(self, path, dialog):
        """Process manually entered path"""
        if path and os.path.exists(path) and path.endswith('.srt'):
            dialog.dismiss()
            self.process_selected_file(path)
        else:
            self.show_error_dialog("Invalid file path or not an SRT file")
    
    def process_selected_file(self, file_path):
        """Process the selected SRT file"""
        if not file_path:
            return
        
        # Show progress dialog
        self.show_progress_dialog("Processing SRT file...")
        
        # Process in background thread
        threading.Thread(
            target=self.process_srt_file,
            args=(file_path,),
            daemon=True
        ).start()
    
    def process_srt_file(self, file_path):
        """Process SRT file and extract words"""
        try:
            from kivymd.app import MDApp
            from utils.settings_manager import get_settings_manager
            # settings = get_settings_manager()
            # srt_lang = settings.get_srt_language()
            # translate_lang = settings.get_translate_language()
            app = MDApp.get_running_app()
            db = app.db_manager
            
            # Add SRT file to database
            filename = os.path.basename(file_path)
            srt_id = db.add_srt_file(filename)
            self.srt_file_name=filename
            # Extract text from SRT
            processor = SRTProcessor()
            lines = processor.clean_srt(file_path)
            
            if not lines:
                raise Exception("No text found in SRT file")
            
            text = processor.get_text_from_lines(lines)
            settings = get_settings_manager()
            api_key = settings.get_next_api_key()
            if api_key:
                gemini = GeminiService(api_key)
            else:
                raise Exception("No API key configured")
            # Get important words using Gemini
            words = gemini.extract_important_words(text)
            
            if not words:
                raise Exception("No words extracted from text")
            
            # Filter out known words
            known_words = set(db.get_all_known_words())
            filtered_words = processor.filter_known_words(words, known_words)
            
            if not filtered_words:
                Clock.schedule_once(
                    lambda dt: self.show_info_dialog(
                        "All Known",
                        "All extracted words are already in your known words list!"
                    ),
                    0
                )
                Clock.schedule_once(lambda dt: self.close_progress_dialog(), 0)
                return
            
            # Navigate to word list screen
            Clock.schedule_once(
                lambda dt: self.navigate_to_word_list(srt_id, filtered_words),
                0
            )
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Error processing SRT: {error_msg}")
            print(traceback.format_exc())
            Clock.schedule_once(
                lambda dt: self.show_error_dialog(f"Processing error: {error_msg}"),
                0
            )
            Clock.schedule_once(lambda dt: self.close_progress_dialog(), 0)
    
    def navigate_to_word_list(self, srt_id, words):
        """Navigate to word list screen"""
        self.close_progress_dialog()
        word_list_screen = self.manager.get_screen('word_list')
        word_list_screen.set_words(srt_id, words)
        self.manager.current = 'word_list'
    
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
    
    def show_info_dialog(self, title, message):
        """Show info dialog"""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def open_library(self):
        """Navigate to SRT library"""
        self.manager.current = 'srt_library'
    
    def open_known_words(self):
        """Navigate to known words screen"""
        self.manager.current = 'known_words'
    
    def open_settings(self):
        """Navigate to settings screen"""
        self.manager.current = 'settings'