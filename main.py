import sys
import os
import signal
import keyboard
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from ui import TranslationPopup, SnippingCanvas

# signal emitter
class HotkeySignaler(QObject):
    show_canvas_signal = pyqtSignal()
    quit_signal = pyqtSignal()

# temporary quit
def quit_program():
    print("Shutting down Snipping Translator...")
    keyboard.unhook_all() # stop keyboard
    QApplication.instance().quit() # stop pyqt gui
    os._exit(0)

# single instance lock
if __name__ == '__main__':
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "RTranslate_SingleInstance_Mutex")
    
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.user32.MessageBoxW(0, "RTranslate is already running in the background!\n\nIf you want to restart it, press [Ctrl + Alt + Q] first to close the old one.", "RTranslate", 48)
        sys.exit(0) 

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    
    signal.signal(signal.SIGINT, signal.SIG_DFL) 
    
    popup = TranslationPopup()
    canvas = SnippingCanvas(popup)
    signaler = HotkeySignaler()

    # connect gui to signaler
    signaler.show_canvas_signal.connect(canvas.activate_canvas)
    signaler.quit_signal.connect(quit_program)

    # emit signal when the key is pressed
    keyboard.add_hotkey('ctrl+alt+t', signaler.show_canvas_signal.emit)
    keyboard.add_hotkey('ctrl+alt+q', signaler.quit_signal.emit)
    
    print("RTranslator is running in the background.")
    
    # welcome popup
    welcome_message = (
        "RTranslate is now running in the background!\n\n"
        "Here are your controls:\n"
        "• [Ctrl + Alt + T] : Draw a box to translate text\n"
        "• [Esc] : Close the translation popup or cancel a snip\n"
        "• [Ctrl + Alt + Q] : Completely shut down the program"
    )
    
    # intruction box show
    ctypes.windll.user32.MessageBoxW(0, welcome_message, "RTranslate Started", 64)
    
    # start (return 0 or 1)
    sys.exit(app.exec())