import os
import sys
import requests
import deepl
import pytesseract
import ctypes # added to show native windows error popups

def get_base_path():
    """Get the correct folder path whether running as script or .exe"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

tesseract_exe = os.path.join(get_base_path(), "Tesseract-OCR", "tesseract.exe")

if not os.path.exists(tesseract_exe):
    # Show a visible error box before crashing
    ctypes.windll.user32.MessageBoxW(0, "Tesseract folder not found! Make sure the 'Tesseract-OCR' folder is next to RTranslate.exe.", "RTranslate Error", 16)
    sys.exit(1)

pytesseract.pytesseract.tesseract_cmd = tesseract_exe


# api key setup
key_file_path = os.path.join(get_base_path(), "api_key.txt")
DEEPL_API_KEY = ""

# check if the text file exists
if os.path.exists(key_file_path):
    with open(key_file_path, "r", encoding="utf-8") as f:
        DEEPL_API_KEY = f.read().strip()

# if the file doesnt exist, or they left it empty / at the default text
if not DEEPL_API_KEY or DEEPL_API_KEY == "PASTE_YOUR_DEEPL_API_KEY_HERE":
    # auto-create the file for them to make it easy
    with open(key_file_path, "w", encoding="utf-8") as f:
        f.write("REPLACE_THIS_TEXT_WITH_YOUR_DEEPL_API_KEY")
    
    # show a warning box
    ctypes.windll.user32.MessageBoxW(0, "First time setup: I just created an 'api_key.txt' file next to the program.\n\nPlease open it, paste your DeepL API key inside, save it, and run me again!", "RTranslate Setup", 64)
    sys.exit(0) # Close the app so they can go edit the file

# initialize deepL translator
try:
    translator = deepl.Translator(DEEPL_API_KEY)
    usage = translator.get_usage() 
    
except Exception as e:
    ctypes.windll.user32.MessageBoxW(0, f"Invalid DeepL API Key!\n\nPlease check your api_key.txt file and make sure there are no spaces.\n\nError: {str(e)}", "RTranslate Error", 16)
    sys.exit(1)


# dictionary fetch
def get_dictionary_data(word):
    clean_word = "".join(c for c in word if c.isalnum() or c.isspace()).strip()
    if len(clean_word.split()) > 3 or len(clean_word) == 0:
        return "", []
    
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{clean_word}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            
            # get definition
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            
            # get synonyms
            synonyms = []
            for meaning in data[0].get('meanings', []):
                synonyms.extend(meaning.get('synonyms', []))
            
            # remove duplicates and grab top 3
            synonyms = list(dict.fromkeys(synonyms))[:3]
            return definition, synonyms
    except Exception:
        pass
    
    return "", []

# translate to thai function
def translate_to_thai(text):
    return translator.translate_text(text, target_lang="TH").text