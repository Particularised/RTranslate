# RTranslate
> Translate any word in real time on your screen with OCR and DeepL API. Perfect for reading documents, reading novels/visual novels. Unfortunately, only EN to TH is available as of now because I initially intended this to be used for personal purposes. I'll update later if I got time. (UI are vibe coded so expect inconsistencies)

## Installation

### Clone the repository:
```
git clone https://github.com/Particularised/RTranslate.git
cd RTranslate
```

### Install Python dependencies:
```
pip install -r requirements.txt
```

### Set up your API Key:
[Get an API key from DeepL](https://www.deepl.com/en/pro/change-plan#api) (Any plan you want or able to afford).
Create a new file in the folder and name it exactly `.env` (the dot at the beginning is required).

*(Note: A `.env` file is a hidden configuration file used to securely store private API keys so they don't accidentally get uploaded to public websites).*

Open the `.env` file with Notepad or any text editor, and paste your key using this exact format:
```
DEEPL_API_KEY=your_actual_api_key_goes_here
```

## How to Use
Run the application:
```
python main.py
```

`Ctrl + Alt + T`: Freeze the screen and draw a translation box. (Press again while open to start a new snip).

`Esc`: Close the popup and return to Windows.

`Ctrl + Alt + Q`: Completely shut down the application running in the background.
