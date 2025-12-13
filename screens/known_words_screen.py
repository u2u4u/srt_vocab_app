"""
Known Words Screen - Optimized Version
Manage the list of known words with RecycleView
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty

Builder.load_string('''
<KnownWordItem>:
    size_hint_y: None
    height: dp(56)
    
    MDCard:
        orientation: 'horizontal'
        padding: [dp(16), dp(8)]
        elevation: 1
        ripple_behavior: True
        on_release: root.delete_word()
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(16)
            
            MDIcon:
                icon: "check-circle"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                size_hint: None, None
                size: dp(32), dp(32)
                pos_hint: {'center_y': 0.5}
            
            MDLabel:
                text: root.word_text
                font_style: "Body1"
                pos_hint: {'center_y': 0.5}
            
            MDIcon:
                icon: "delete"
                size_hint: None, None
                size: dp(32), dp(32)
                pos_hint: {'center_y': 0.5}

<KnownWordsScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Known Words"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["plus", lambda x: root.show_add_dialog()]]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            
            MDTextField:
                id: search_field
                hint_text: "Search known words"
                icon_right: "magnify"
                size_hint_y: None
                height: dp(48)
                on_text: root.filter_words(self.text)
            
            MDCard:
                size_hint_y: None
                height: dp(40)
                padding: dp(10)
                elevation: 1
                
                MDLabel:
                    id: count_label
                    text: root.count_text
                    font_style: "Caption"
                    halign: "center"
            
            RecycleView:
                id: known_words_recycler
                viewclass: 'KnownWordItem'
                
                RecycleBoxLayout:
                    default_size: None, dp(56)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    spacing: dp(2)
''')

class KnownWordItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable known word item"""
    word_text = StringProperty()
    index = None
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when the view is being recycled"""
        self.index = index
        self.word_text = data['word']
        return super().refresh_view_attrs(rv, index, data)
    
    def delete_word(self):
        """Show confirmation before deleting"""
        screen = self.get_root_window().children[0].current_screen
        if hasattr(screen, 'confirm_delete'):
            screen.confirm_delete(self.word_text)

class KnownWordsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_words = []
        self.filtered_words = []
        self.add_dialog = None
    
    @property
    def count_text(self):
        return f"{len(self.all_words)} known words"
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_known_words()
    
    def load_known_words(self):
        """Load known words from database"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        self.all_words = db.get_all_known_words()
        self.filtered_words = self.all_words.copy()
        self.populate_list()
        self.update_count()
    
    def populate_list(self):
        """Populate the RecycleView with words"""
        self.ids.known_words_recycler.data = [
            {'word': word} for word in self.filtered_words
        ]
    
    def update_count(self):
        """Update the count label"""
        if hasattr(self.ids, 'count_label'):
            self.ids.count_label.text = self.count_text
    
    def filter_words(self, search_text):
        """Filter words based on search"""
        if not search_text:
            self.filtered_words = self.all_words.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_words = [
                w for w in self.all_words 
                if search_lower in w.lower()
            ]
        
        self.populate_list()
    
    def show_add_dialog(self):
        """Show dialog to add new known word"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80)
        )
        
        text_field = MDTextField(
            hint_text="Enter word",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(text_field)
        
        dialog = MDDialog(
            title="Add Known Word",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=lambda x: self.add_word(text_field.text, dialog)
                ),
            ],
        )
        dialog.open()
    
    def add_word(self, word, dialog):
        """Add word to known words"""
        if not word or not word.strip():
            return
        
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        if db.add_known_word(word.strip()):
            dialog.dismiss()
            # Reload data
            Clock.schedule_once(lambda dt: self.load_known_words(), 0)
        else:
            # Word already exists - show message
            self.show_info_dialog("Already Exists", f"'{word}' is already in your known words list.")
    
    def confirm_delete(self, word):
        """Confirm before deleting word"""
        dialog = MDDialog(
            title="Remove Word",
            text=f"Remove '{word}' from known words?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="REMOVE",
                    on_release=lambda x: self.delete_word(word, dialog)
                ),
            ],
        )
        dialog.open()
    
    def delete_word(self, word, dialog):
        """Delete word from known words"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        db = app.db_manager
        
        db.remove_known_word(word)
        dialog.dismiss()
        
        # Update lists
        if word in self.all_words:
            self.all_words.remove(word)
        if word in self.filtered_words:
            self.filtered_words.remove(word)
        
        # Update UI
        Clock.schedule_once(lambda dt: self.populate_list(), 0)
        Clock.schedule_once(lambda dt: self.update_count(), 0)
    
    def show_info_dialog(self, title, text):
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
        dialog.open()
    
    def go_back(self):
        """Go back to home"""
        self.manager.current = 'home'