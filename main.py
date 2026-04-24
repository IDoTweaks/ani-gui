import sys
# Add these PyQt6 imports for animations and text inputs
from PyQt6.QtWidgets import QLineEdit, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from database import init_db, update_history
from player import play_episode
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QScrollArea, QGridLayout, 
                             QStackedWidget, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests

from api import fetch_anime
from components import AnimeCard

class AniGui(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize the SQLite database
        init_db()
        
        self.setWindowTitle("Ani-CLI GUI")
        self.setGeometry(100, 100, 1100, 700)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #141414; }
            QScrollArea { border: none; background-color: transparent; }
            QWidget#sidebar { background-color: #0d0d0d; }
            QPushButton {
                background-color: transparent; color: #b3b3b3;
                text-align: left; padding: 12px 20px;
                font-size: 16px; font-weight: bold; border-radius: 5px;
            }
            QPushButton:hover { color: white; background-color: #2b2b2b; }
            QComboBox {
                background-color: #333; color: white;
                padding: 5px; border-radius: 3px; font-size: 14px;
            }
            QPushButton#playBtn {
                background-color: #E50914; color: white;
                text-align: center; border-radius: 5px; font-size: 18px; padding: 10px;
            }
            QPushButton#playBtn:hover { background-color: #f40612; }
            QPushButton#backBtn {
                background-color: #333; text-align: center; width: 100px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_label = QLabel("<b>Ani-GUI</b>")
        title_label.setStyleSheet("font-size: 28px; color: #E50914; padding: 20px 10px;")
        
        self.btn_home = QPushButton("🏠  Home")
        self.btn_home.clicked.connect(self.show_home) 
        
        # Search Bar (Moved down here so the layout exists first!)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search anime...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #333; color: white;
                padding: 10px; border-radius: 5px; margin: 10px;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.search_input) # Added properly
        sidebar_layout.addWidget(QPushButton("📺  Watchlist"))
        sidebar_layout.addSpacing(500)

        # --- Stacked Widget (To switch between Grid and Details) ---
        self.stacked_widget = QStackedWidget()

        # Page 1: The Grid
        self.grid_page = QWidget()
        self.grid_layout = QGridLayout(self.grid_page)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(30, 30, 30, 30)
        
        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setWidget(self.grid_page)
        self.stacked_widget.addWidget(grid_scroll)

        # Page 2: Show Details
        self.details_page = QWidget()
        self.build_details_page()
        self.stacked_widget.addWidget(self.details_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        # Load Initial Data
        self.load_dashboard()

    def build_details_page(self):
        """Builds the layout for the details page."""
        layout = QVBoxLayout(self.details_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)

        # Back Button
        back_btn = QPushButton("← Back to Grid")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(self.show_home)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Top Section (Poster + Info)
        top_section = QHBoxLayout()
        
        self.detail_image = QLabel()
        self.detail_image.setFixedSize(225, 315)
        self.detail_image.setStyleSheet("background-color: #222; border-radius: 8px;")
        self.detail_image.setScaledContents(True)
        
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.detail_title = QLabel("Title")
        self.detail_title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        
        self.detail_synopsis = QLabel("Synopsis goes here...")
        self.detail_synopsis.setWordWrap(True)
        self.detail_synopsis.setStyleSheet("font-size: 14px; color: #b3b3b3; margin-top: 10px;")
        
        # --- Grouping Options (Seasons & Sub/Dub) ---
        options_layout = QHBoxLayout()
        
        self.season_combo = QComboBox()
        self.season_combo.addItems(["Season 1", "Season 2", "Season 3", "Season 4", "Season 5"]) 
        
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Sub", "Dub"])
        
        options_layout.addWidget(QLabel("<b>Season:</b>"), alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.season_combo)
        options_layout.addWidget(QLabel("<b>Audio:</b>"), alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.audio_combo)
        options_layout.addStretch() 
        
        # Fixed Play Button 
        self.play_btn = QPushButton("▶ Play Episode 1")
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedWidth(200)
        self.play_btn.clicked.connect(self.trigger_play)

        info_layout.addWidget(self.detail_title)
        info_layout.addLayout(options_layout)
        info_layout.addWidget(self.play_btn) # Added the correct button
        info_layout.addWidget(self.detail_synopsis)
        
        top_section.addWidget(self.detail_image)
        top_section.addLayout(info_layout)
        
        layout.addLayout(top_section)

    def load_dashboard(self):
        anime_list = fetch_anime()
        
        row, col = 0, 0
        for anime in anime_list:
            card = AnimeCard(anime) 
            card.clicked.connect(self.open_details) 
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

    def open_details(self, anime_data):
        """Updates the details page with the clicked anime's info and switches to it."""
        self.current_anime_data = anime_data # Save this so the Play button can access it!
        
        self.detail_title.setText(anime_data["title"])
        self.detail_synopsis.setText(anime_data["synopsis"])
        
        # Load the high-res image
        img_data = requests.get(anime_data["image_url"]).content
        pixmap = QPixmap()
        pixmap.loadFromData(img_data)
        self.detail_image.setPixmap(pixmap)
        
        # Flip to the details page with animation
        self.stacked_widget.setCurrentIndex(1)
        self.effect = QGraphicsOpacityEffect(self.details_page)
        self.details_page.setGraphicsEffect(self.effect)
        
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(400) 
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def show_home(self):
        """Flips back to the grid page."""
        self.stacked_widget.setCurrentIndex(0)

    def perform_search(self):
        query = self.search_input.text()
        if not query:
            return
            
        # Clear the current grid
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        # Fetch new data
        anime_list = fetch_anime(query=query)
        
        row, col = 0, 0
        for anime in anime_list:
            card = AnimeCard(anime)
            card.clicked.connect(self.open_details)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def trigger_play(self):
        title = self.detail_title.text()
        season = self.season_combo.currentText()
        episode = 1 
        
        # Save to SQLite History
        image_url = self.current_anime_data["image_url"]
        update_history(title, image_url, season, episode)
        
        # Launch ani-cli
        play_episode(title, episode)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AniGui()
    window.show()
    sys.exit(app.exec())