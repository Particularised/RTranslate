import sys
import signal
import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from ui import TranslationPopup, SnippingCanvas

# signal emitter
class HotkeySignaler(QObject):
    show_canvas_signal = pyqtSignal()

# temporary quit
def quit_program():
    print("Shutting down Snipping Translator...")
    keyboard.unhook_all() # stop keyboard
    QApplication.instance().quit() # stop pyqt gui
    sys.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL) 
    
    popup = TranslationPopup()
    canvas = SnippingCanvas(popup)
    signaler = HotkeySignaler()

    # connect gui to signaler
    signaler.show_canvas_signal.connect(canvas.activate_canvas)

    # emit signal when the key is pressed
    keyboard.add_hotkey('ctrl+alt+t', signaler.show_canvas_signal.emit)
    keyboard.add_hotkey('ctrl+alt+q', quit_program)
    
    print("RTranslator is running.")
    print("Press Ctrl+Alt+T to start snipping, Ctrl+Alt+Q to close the program entirely.")
    
    # start (return 0 or 1)
    sys.exit(app.exec())