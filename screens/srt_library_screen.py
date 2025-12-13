"""
SRT Library Screen - Complete with Delete Function
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

class SRTLibraryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_dialog = None
    
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