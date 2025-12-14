"""
Settings Screen
Manage application settings including API keys
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
from utils.settings_manager import get_settings_manager

Builder.load_string('''
<APIKeyItem>:
    size_hint_y: None
    height: dp(72)
    
    MDCard:
        orientation: 'horizontal'
        padding: [dp(16), dp(8)]
        elevation: 2
        
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(16)
            
            MDIcon:
                icon: "key"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}
            
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(4)
                
                MDLabel:
                    text: root.masked_key
                    font_style: "Body1"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    text: root.key_info
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: self.texture_size[1]
            
            MDIconButton:
                icon: "delete"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                size_hint: None, None
                size: dp(40), dp(40)
                pos_hint: {'center_y': 0.5}
                on_release: root.delete_key()

<SettingsScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Settings"
            elevation: 2
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        
        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(20)
                adaptive_height: True
                
                # API Keys Section
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(15)
                    size_hint_y: None
                    height: dp(400)
                    elevation: 3
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "API Keys"
                            font_style: "H6"
                            size_hint_x: 0.7
                        
                        MDRaisedButton:
                            text: "Add Key"
                            size_hint_x: 0.3
                            on_release: root.show_add_key_dialog()
                    
                    MDLabel:
                        text: root.keys_info
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: dp(30)
                    
                    MDSeparator:
                        height: dp(1)
                    
                    RecycleView:
                        id: keys_recycler
                        viewclass: 'APIKeyItem'
                        
                        RecycleBoxLayout:
                            default_size: None, dp(72)
                            default_size_hint: 1, None
                            size_hint_y: None
                            height: self.minimum_height
                            orientation: 'vertical'
                            spacing: dp(8)
                
                # Language Settings Card
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(15)
                    size_hint_y: None
                    height: dp(265)
                    elevation: 3
                    
                    MDLabel:
                        text: "Language Settings"
                        font_style: "H6"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDSeparator:
                        height: dp(1)
                    
                    MDTextField:
                        id: srt_language_field
                        hint_text: "SRT Language"
                        text: root.srt_language
                        helper_text: "Source language of subtitle files"
                        helper_text_mode: "on_focus"
                        size_hint_y: None
                        height: dp(63)
                        on_text_validate: root.update_srt_language(self.text)
                    
                    MDTextField:
                        id: translate_language_field
                        hint_text: "Translation Language"
                        text: root.translate_language
                        helper_text: "Target language for word meanings"
                        helper_text_mode: "on_focus"
                        size_hint_y: None
                        height: dp(63)
                        on_text_validate: root.update_translate_language(self.text)
                    
                    MDLabel:
                        text: "Press Enter to save changes"
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: dp(20)
                
                # Info Card
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(200)
                    elevation: 2
                    
                    MDLabel:
                        text: "About API Keys"
                        font_style: "Subtitle1"
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDLabel:
                        text: "• Keys are used in rotation to avoid rate limits"
                        font_style: "Body2"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDLabel:
                        text: "• Get your key from Google AI Studio"
                        font_style: "Body2"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDLabel:
                        text: "• Multiple keys = better performance"
                        font_style: "Body2"
                        size_hint_y: None
                        height: self.texture_size[1]
                    
                    MDRaisedButton:
                        text: "Get API Key"
                        size_hint_x: 0.5
                        pos_hint: {'center_x': 0.5}
                        on_release: root.open_api_key_url()
''')

class APIKeyItem(RecycleDataViewBehavior, MDBoxLayout):
    """Recyclable API key item"""
    masked_key = StringProperty()
    key_info = StringProperty()
    full_key = StringProperty()
    index = None
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when the view is being recycled"""
        self.index = index
        self.full_key = data['key']
        self.masked_key = self.mask_key(data['key'])
        self.key_info = f"Key #{index + 1}"
        return super().refresh_view_attrs(rv, index, data)
    
    def mask_key(self, key: str) -> str:
        """Mask API key for security"""
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    def delete_key(self):
        """Delete this API key"""
        screen = self.get_root_window().children[0].current_screen
        if hasattr(screen, 'confirm_delete_key'):
            screen.confirm_delete_key(self.full_key)

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_manager = get_settings_manager()
        self.add_dialog = None
    
    @property
    def keys_info(self):
        count = self.settings_manager.get_api_key_count()
        if count == 0:
            return "No API keys configured. Add at least one to use the app."
        elif count == 1:
            return "1 API key configured"
        else:
            return f"{count} API keys configured (will be used in rotation)"
    
    @property
    def srt_language(self):
        return self.settings_manager.get_srt_language()

    @property
    def translate_language(self):
        return self.settings_manager.get_translate_language()
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_api_keys()
        # Update language fields
        if hasattr(self.ids, 'srt_language_field'):
            self.ids.srt_language_field.text = self.srt_language
        if hasattr(self.ids, 'translate_language_field'):
            self.ids.translate_language_field.text = self.translate_language
    
    def load_api_keys(self):
        """Load API keys from settings"""
        keys = self.settings_manager.get_api_keys()
        self.populate_keys_list(keys)
    
    def populate_keys_list(self, keys):
        """Populate the RecycleView with API keys"""
        self.ids.keys_recycler.data = [
            {'key': key} for key in keys
        ]
    
    def update_srt_language(self, language):
        """Update SRT language setting"""
        if language and language.strip():
            if self.settings_manager.set_srt_language(language.strip()):
                self.show_toast(f"SRT language set to: {language}")
            else:
                self.show_toast("Failed to update SRT language")

    def update_translate_language(self, language):
        """Update translation language setting"""
        if language and language.strip():
            if self.settings_manager.set_translate_language(language.strip()):
                self.show_toast(f"Translation language set to: {language}")
            else:
                self.show_toast("Failed to update translation language")
    
    def show_add_key_dialog(self):
        """Show dialog to add new API key"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )
        
        text_field = MDTextField(
            hint_text="Enter API Key",
            helper_text="Paste your Google AI Studio API key",
            helper_text_mode="on_focus",
            size_hint_y=None,
            height=dp(48),
            multiline=False
        )
        content.add_widget(text_field)
        
        info_label = MDLabel(
            text="The key will be stored securely in settings.json",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(info_label)
        
        dialog = MDDialog(
            title="Add API Key",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    on_release=lambda x: self.add_api_key(text_field.text, dialog)
                ),
            ],
        )
        dialog.open()
    
    def add_api_key(self, key, dialog):
        """Add API key to settings"""
        if not key or not key.strip():
            self.show_toast("Please enter a valid API key")
            return
        
        # Basic validation
        key = key.strip()
        if len(key) < 20:
            self.show_toast("API key seems too short")
            return
        
        if self.settings_manager.add_api_key(key):
            dialog.dismiss()
            self.show_toast("API key added successfully!")
            Clock.schedule_once(lambda dt: self.load_api_keys(), 0)
        else:
            self.show_toast("This API key already exists")
    
    def confirm_delete_key(self, key):
        """Confirm before deleting API key"""
        masked = self.mask_key_static(key)
        
        dialog = MDDialog(
            title="Remove API Key",
            text=f"Remove key {masked}?\n\nThis cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="REMOVE",
                    on_release=lambda x: self.delete_api_key(key, dialog)
                ),
            ],
        )
        dialog.open()
    
    def delete_api_key(self, key, dialog):
        """Delete API key from settings"""
        if self.settings_manager.remove_api_key(key):
            dialog.dismiss()
            self.show_toast("API key removed")
            Clock.schedule_once(lambda dt: self.load_api_keys(), 0)
        else:
            self.show_toast("Failed to remove API key")
    
    @staticmethod
    def mask_key_static(key: str) -> str:
        """Mask API key for security"""
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    def show_toast(self, message):
        """Show a quick toast message"""
        from kivymd.toast import toast
        toast(message)
    
    def open_api_key_url(self):
        """Open Google AI Studio in browser"""
        import webbrowser
        webbrowser.open("https://makersuite.google.com/app/apikey")
    
    def go_back(self):
        """Go back to home"""
        self.manager.current = 'home'