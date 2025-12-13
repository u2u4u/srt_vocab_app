# SRT Vocabulary Extractor

A complete application for extracting and learning vocabulary from SRT subtitle files using AI.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install kivy==2.3.0
pip install kivymd==1.2.0
pip install google-genai
```

### 2. Set Up Project Structure

Create the following folder structure:

```
srt_vocab_app/
├── main.py
├── requirements.txt
├── test_setup.py          # Test your installation
├── quick_test.py          # Test database threading
│
├── database/
│   ├── __init__.py
│   └── db_manager.py
│
├── processors/
│   ├── __init__.py
│   └── srt_processor.py
│
├── services/
│   ├── __init__.py
│   └── gemini_service.py
│
├── screens/
│   ├── __init__.py
│   ├── home_screen.py
│   ├── word_list_screen.py
│   ├── known_words_screen.py
│   └── srt_library_screen.py
│
└── utils/
    ├── __init__.py
    └── file_handler.py
```

### 3. Create Empty `__init__.py` Files

```bash
# On Linux/Mac:
touch database/__init__.py
touch processors/__init__.py
touch services/__init__.py
touch screens/__init__.py
touch utils/__init__.py

# On Windows (PowerShell):
New-Item database/__init__.py -ItemType File
New-Item processors/__init__.py -ItemType File
New-Item services/__init__.py -ItemType File
New-Item screens/__init__.py -ItemType File
New-Item utils/__init__.py -ItemType File

# On Windows (Command Prompt):
type nul > database\__init__.py
type nul > processors\__init__.py
type nul > services\__init__.py
type nul > screens\__init__.py
type nul > utils\__init__.py
```

### 4. Test Your Installation

```bash
python test_setup.py
```

This will check:
- Python version
- All dependencies
- Directory structure
- Required files
- Database creation
- Thread safety

### 5. Configure API Key

**IMPORTANT:** Replace the API key in these files:
- `screens/home_screen.py` (line with `GeminiService(...)`)
- `screens/word_list_screen.py` (line with `GeminiService(...)`)

Replace:
```python
gemini = GeminiService("AIzaSyBr2gHO058kDWxBuK6_v9tySIZqsUbY81E")
```

With your own key:
```python
gemini = GeminiService("YOUR_ACTUAL_API_KEY_HERE")
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 6. Run the Application

```bash
cd srt_vocab_app
python main.py
```

## 📋 Features

### ✅ Core Features
- 📤 Upload SRT subtitle files
- 🤖 AI-powered vocabulary extraction (using Google Gemini)
- 📚 Manage known words to filter future extractions
- 🔍 View vocabulary library with meanings and examples
- 💾 SQLite database for persistent storage
- 🎯 Mark words as learned

### 🎨 UI Features
- Material Design interface (KivyMD)
- Multiple screens with smooth navigation
- Progress indicators for long operations
- Search functionality
- Expandable word details

## 🛠️ Troubleshooting

### Error: "SQLite objects created in a thread can only be used in that same thread"
**Solution:** ✅ This is now FIXED in the latest version. The database manager uses thread-local connections.

To verify the fix works:
```bash
python quick_test.py
```

### Error: "Module not found"
**Solution:** Ensure all `__init__.py` files exist in each folder:
```bash
ls -la database/__init__.py
ls -la processors/__init__.py
ls -la services/__init__.py
ls -la screens/__init__.py
ls -la utils/__init__.py
```

### Error: "Invalid syntax in KV file"
**Solution:** This is usually fixed in the latest version. Make sure you're using the "Fixed Version" files provided.

### Error: "API Key not valid"
**Solution:** 
1. Get a valid API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Replace it in both files mentioned above
3. Make sure there are no extra spaces or quotes

### Error: "File chooser not working"
**Solution:** The app will fall back to manual path entry. You can also install `plyer`:
```bash
pip install plyer
```

### Error: "Cannot connect to database"
**Solution:** 
- Make sure you have write permissions in the app directory
- Delete `vocab.db` if it exists and let the app recreate it

## 📱 File Selection Methods

The app supports two methods for file selection:

### Method 1: Plyer (Recommended)
Install plyer for native file dialogs:
```bash
pip install plyer
```

### Method 2: Manual Path Entry (Fallback)
If plyer is not available, you'll be prompted to enter the file path manually.

**Example paths:**
- Windows: `C:\Users\YourName\Downloads\subtitle.srt`
- Linux/Mac: `/home/username/Downloads/subtitle.srt`

## 🔧 Configuration

### Change Theme Colors
Edit in `main.py`:
```python
self.theme_cls.primary_palette = "Blue"  # Try: "Purple", "Red", "Green", etc.
self.theme_cls.primary_hue = "700"       # 50 to 900
self.theme_cls.theme_style = "Light"     # Or "Dark"
```

### Change AI Model
Edit in `services/gemini_service.py`:
```python
model="gemini-2.5-flash"  # Or other available models
```

## 📊 Database Schema

### Tables

**srtfiles**
- `id`: Primary key
- `srtfile`: Filename

**words**
- `id`: Primary key
- `word`: English word
- `meaning`: Persian meaning + examples
- `srtfile`: Foreign key to srtfiles

**known_words**
- `id`: Primary key
- `word`: Known word (unique)

## 🚀 Building for Production

### Android (using Buildozer)
```bash
pip install buildozer
buildozer init
buildozer -v android debug
```

### Desktop (using PyInstaller)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 📝 Usage Workflow

1. **Upload SRT File** → Choose an SRT subtitle file
2. **Review Words** → AI extracts important vocabulary
3. **Mark Known Words** → Remove words you already know
4. **Fetch Meanings** → Get Persian meanings and examples
5. **Study Library** → Review all words by SRT file
6. **Mark Learned** → Move words to known words list

## 🎯 Tips for Best Results

- Use SRT files with natural dialogue (movies, series)
- Review and clean the extracted word list before fetching meanings
- Regularly update your known words list
- The AI learns from context, so better subtitles = better word extraction

## 📦 Dependencies

```
kivy==2.3.0
kivymd==1.2.0
google-genai
plyer (optional, for native file dialogs)
```

## 🤝 Contributing

Feel free to improve the code! Some ideas:
- Add pronunciation audio
- Export to Anki format
- Add spaced repetition quiz
- Cloud sync for known words
- Support for multiple languages

## 📄 License

Free to use and modify for personal and educational purposes.

## 🆘 Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify all dependencies are installed
3. Make sure API key is correctly set
4. Check console output for detailed error messages

---

**Note:** This app requires an active internet connection for AI-powered vocabulary extraction.