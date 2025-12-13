"""
Persian/Arabic Text Helper
Fixes text display for RTL languages
"""

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
    print("✓ Persian text helper: Libraries loaded successfully")
except ImportError as e:
    BIDI_AVAILABLE = False
    print(f"✗ Persian text helper: Libraries not available - {e}")
    print("  Install with: pip install arabic-reshaper python-bidi")

def fix_persian_text(text):
    """
    Fix Persian/Arabic text for display in Kivy
    """
    if not text:
        return text
    
    if not BIDI_AVAILABLE:
        print(f"⚠ Cannot fix text (libraries not available): {text[:20]}...")
        return text
    
    try:
        # Step 1: Reshape the text (connect letters)
        reshaped_text = arabic_reshaper.reshape(text)
        
        # Step 2: Apply bidi algorithm (right-to-left)
        bidi_text = get_display(reshaped_text)
        
        return bidi_text
    except Exception as e:
        print(f"✗ Error fixing Persian text: {e}")
        return text