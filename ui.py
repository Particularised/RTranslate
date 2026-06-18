from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, QPoint, QRect, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PIL import ImageGrab
import pytesseract
from api import get_dictionary_data, translate_to_thai

class TranslationPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas_ref = None 
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # ui elements
        self.layout = QVBoxLayout()
        
        # text labels (Now selectable so you can copy-paste!)
        self.word_label = QLabel("Word")
        self.word_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.word_label.setWordWrap(True)
        self.word_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.synonym_label = QLabel("")
        self.synonym_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.synonym_label.setStyleSheet("color: #aaaaaa;")
        self.synonym_label.setWordWrap(True)
        self.synonym_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.def_label = QLabel("Definition will appear here...")
        self.def_label.setFont(QFont("Segoe UI", 12))
        self.def_label.setWordWrap(True)
        self.def_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.toggle_btn = QPushButton("Translate to Thai")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_language)

        self.footer_label = QLabel("Press [Esc] to close • Press [Ctrl+Alt+T] for new snip")
        self.footer_label.setFont(QFont("Segoe UI", 9))
        self.footer_label.setStyleSheet("color: #777777; margin-top: 10px;")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # add to layout
        self.layout.addWidget(self.word_label)
        self.layout.addWidget(self.synonym_label)
        self.layout.addWidget(self.def_label)
        self.layout.addWidget(self.toggle_btn)
        self.layout.addWidget(self.footer_label)
        self.setLayout(self.layout)
        
        # styling (Added padding-right to QLabel to act as a safety buffer)
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #ffffff; border-radius: 8px; border: 1px solid #444; }
            QPushButton#TranslateBtn { background-color: #3b82f6; color: white; padding: 8px; border-radius: 5px; font-weight: bold; border: none; margin-top: 10px;}
            QPushButton#TranslateBtn:hover { background-color: #2563eb; }
            QLabel { border: none; padding-right: 5px; } 
        """)
        self.toggle_btn.setObjectName("TranslateBtn") 
        
        # data state
        self.is_showing_thai = False
        self.en_word = ""
        self.th_word = ""
        self.en_synonyms = []
        self.en_def = ""
        self.last_x = 0
        self.last_y = 0

    # boundary detection so it never spawns off-screen
    def reposition_safe(self, x, y):
        self.adjustSize()
        screen = QApplication.primaryScreen().availableGeometry()
        
        if x + self.width() > screen.width():
            x = screen.width() - self.width() - 20
        if y + self.height() > screen.height():
            y = screen.height() - self.height() - 20
            
        x = max(20, x)
        y = max(20, y)
        self.move(x, y)

    def show_loading(self, x, y):
        self.last_x, self.last_y = x, y
        self.word_label.setText("Processing...")
        self.synonym_label.hide()
        self.def_label.setText("Please wait a moment.")
        self.toggle_btn.hide()
        self.footer_label.hide()
        self.update_ui()
        self.show()

    def set_data(self, en_word, th_word, en_synonyms, en_def):
        self.en_word = en_word
        self.th_word = th_word
        self.en_synonyms = en_synonyms
        self.en_def = en_def
        self.is_showing_thai = False
        self.update_ui()
        self.toggle_btn.show()
        self.footer_label.show()

    def toggle_language(self):
        self.is_showing_thai = not self.is_showing_thai
        self.update_ui()

    def update_ui(self):
        if self.is_showing_thai:
            self.word_label.setText(self.th_word)
            self.toggle_btn.setText("Show Original English")
            self.def_label.hide() 
            self.synonym_label.hide()
        else:
            self.word_label.setText(self.en_word)
            self.toggle_btn.setText("Translate to Thai")
            self.def_label.setText(self.en_def)
            self.def_label.show()
            if self.en_synonyms:
                self.synonym_label.setText(f"Similar: {', '.join(self.en_synonyms)}")
                self.synonym_label.show()
            else:
                self.synonym_label.hide()
        
        # --- FIX: The Collapse-and-Expand Wrapping Algorithm ---
        
        # 1. Lower label minimum sizes to force PyQt to wrap Asian text characters
        self.word_label.setMinimumWidth(10)
        self.def_label.setMinimumWidth(10)
        self.synonym_label.setMinimumWidth(10)

        # 2. Release any fixed width limits (INCREASED MAX WIDTH TO 800)
        self.setMinimumWidth(300)
        self.setMaximumWidth(800)
        
        # 3. Collapse the window mathematically (forces a layout refresh)
        self.resize(1, 1)
        
        # 4. Let PyQt expand it naturally up to the new 800px limit
        self.adjustSize()
        
        # 5. Lock the final width so the UI feels solid
        self.setFixedWidth(self.width())

        self.reposition_safe(self.last_x, self.last_y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            if self.canvas_ref:
                self.canvas_ref.hide()

class SnippingCanvas(QWidget):
    def __init__(self, popup_ref):
        super().__init__()
        self.popup = popup_ref
        self.popup.canvas_ref = self 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.4)
        self.begin_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

    def activate_canvas(self):
        if self.isVisible():
            self.popup.hide()
            self.is_drawing = False
            self.begin_point = QPoint()
            self.end_point = QPoint()
            self.update() 
        else:
            self.showFullScreen()

    def mousePressEvent(self, event):
        # if the popup is showing, clicking the dim background closes the app entirely
        if self.popup.isVisible():
            self.hide()
            self.popup.hide()
            return
            
        self.begin_point = event.pos()
        self.end_point = self.begin_point
        self.is_drawing = True
        self.update()

    def mouseMoveEvent(self, event):
        # only update the drawing box if we are actually drawing
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_drawing:
            self.is_drawing = False
            capture_box = QRect(self.begin_point, self.end_point).normalized() # normalize so pillow wont freak out somehow
            self.update() 
            QApplication.processEvents() # process the upper line before proceeding
            if capture_box.width() > 0 and capture_box.height() > 0:
                bbox = (capture_box.left(), capture_box.top(), capture_box.right(), capture_box.bottom())
                self.popup.show_loading(capture_box.left(), capture_box.bottom() + 10)
                QApplication.processEvents() # process the upper line before proceeding
                screenshot = ImageGrab.grab(bbox) # ss
                try:
                    extracted_text = pytesseract.image_to_string(screenshot, lang='eng').strip(' \t\n\r"\'.,;!?-')
                    if not extracted_text:
                        self.popup.set_data("Error", "ข้อผิดพลาด", [], "No text found in image.")
                        return
                    en_def, en_synonyms = get_dictionary_data(extracted_text)
                    if not en_def:
                        en_def = "(No dictionary definition found.)"
                    th_word = translate_to_thai(extracted_text)
                    self.popup.set_data(extracted_text, th_word, en_synonyms, en_def)
                except Exception as e:
                    self.popup.set_data("API Error", "ข้อผิดพลาด", [], str(e))

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.is_drawing and not self.popup.isVisible():
            painter.setPen(QPen(QColor(255, 255, 255, 120)))
            painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Draw a box to translate\nPress [Esc] to cancel\nPress [Ctrl+Alt+Q] to close the program entirely.")
        if self.is_drawing:
            pen = QPen(QColor(255, 255, 255), 2)
            painter.setPen(pen)
            capture_box = QRect(self.begin_point, self.end_point).normalized()
            painter.drawRect(capture_box)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.popup.hide()