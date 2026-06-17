RTranslate
Translate any word in real time on your screen with OCR and DeepL API. Perfect for reading documents, reading novels/visual novels. Unfortunately, only EN to TH is available as of now because initially I intended for personal purposes. I'll update later if I got time.

Installation

Clone the repository:
git clone [https://github.com/Particularised/RTranslate.git](https://github.com/Particularised/RTranslate.git)
cd RTranslate

Install Python dependencies:
pip install -r requirements.txt

Set up your API Key:
Get a free API key from DeepL Pro (Free Tier).
Make a copy of the .env.example file and rename it to .env.
Paste your DeepL key into the .env file.

How to Use
Run the application:
python main.py

Ctrl + Alt + T: Freeze the screen and draw a translation box. (Press again while open to start a new snip).
Click the Dim Screen: Close the translation popup and return to Windows.
Esc: Close the popup and return to Windows.
Ctrl + Alt + Q: Completely shut down the application running in the background.