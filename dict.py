import os
import requests
import deepl
import pytesseract
from dotenv import load_dotenv

# load
load_dotenv()
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'

# fetch key
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

if not DEEPL_API_KEY:
    raise ValueError("DeepL API Key not found! Please check your .env file.")

translator = deepl.Translator(DEEPL_API_KEY)

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