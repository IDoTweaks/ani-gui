import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QColor, QFont, QCursor
from PyQt6.QtCore import Qt, pyqtSignal

class AnimeCard(QWidget):
    # This is a custom signal that will "shout" the anime data when clicked
    clicked = pyqtSignal(dict)

    def __init__(self, anime_data):
        super().__init__()
        self.anime_data = anime_data # Store the data (title, image, synopsis)
        
        self.setFixedSize(180, 280)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # --- Poster Image ---
        self.image_label = QLabel()
        self.image_label.setFixedSize(160, 225)
        self.image_label.setStyleSheet("background-color: #222; border-radius: 8px;")
        self.image_label.setScaledContents(True)
        
        try:
            img_data = requests.get(anime_data["image_url"]).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.image_label.setPixmap(pixmap)
        except Exception:
            self.image_label.setText("Image Error")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        # --- Title ---
        self.title_label = QLabel(anime_data["title"])
        self.title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #e5e5e5;")
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- Drop Shadow ---
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)

    # When the user clicks the card, emit the signal with the anime data
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.anime_data)