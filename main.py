import sys
from PyQt6.QtWidgets import QLineEdit, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from database import init_db, update_history, get_history, get_last_watched_episode 
# ---> Notice we import fetch_ani_cli_seasons now
from player import play_episode, fetch_ani_cli_seasons 
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QScrollArea, QGridLayout, 
                             QStackedWidget, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests

from api import fetch_anime
from components import AnimeCard

class AniGui(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        
        self.setWindowTitle("Ani-CLI GUI")
        self.setGeometry(100, 100, 1100, 700)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #141414; }
            QScrollArea { border: none; background-color: transparent; }
            QWidget#sidebar { background-color: #0d0d0d; }
            QPushButton {
                background-color: transparent; color: #b3b3b3; text-align: left; 
                padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 5px;
            }
            QPushButton:hover { color: white; background-color: #2b2b2b; }
            QComboBox, QSpinBox {
                background-color: #333; color: white; padding: 5px; border-radius: 3px; font-size: 14px;
            }
            QPushButton#playBtn {
                background-color: #E50914; color: white; text-align: center; 
                border-radius: 5px; font-size: 18px; padding: 10px;
            }
            QPushButton#playBtn:hover { background-color: #f40612; }
            QPushButton#backBtn { background-color: #333; text-align: center; width: 100px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_label = QLabel("<b>Ani-GUI</b>")
        title_label.setStyleSheet("font-size: 28px; color: #E50914; padding: 20px 10px;")
        
        self.btn_home = QPushButton("🏠  Home")
        self.btn_home.clicked.connect(self.show_home) 
        
        self.btn_continue = QPushButton("⏱️  Continue")
        self.btn_continue.clicked.connect(self.show_continue)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search anime...")
        self.search_input.setStyleSheet("QLineEdit { background-color: #333; color: white; padding: 10px; border-radius: 5px; margin: 10px; }")
        self.search_input.returnPressed.connect(self.perform_search)
        
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_continue)
        sidebar_layout.addWidget(self.search_input)
        sidebar_layout.addSpacing(500)

        self.stacked_widget = QStackedWidget()

        self.grid_page = QWidget()
        self.grid_layout = QGridLayout(self.grid_page)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(30, 30, 30, 30)
        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setWidget(self.grid_page)
        self.stacked_widget.addWidget(grid_scroll)

        self.details_page = QWidget()
        self.build_details_page()
        self.stacked_widget.addWidget(self.details_page)

        self.continue_page = QWidget()
        self.continue_layout = QGridLayout(self.continue_page)
        self.continue_layout.setSpacing(20)
        self.continue_layout.setContentsMargins(30, 30, 30, 30)
        continue_scroll = QScrollArea()
        continue_scroll.setWidgetResizable(True)
        continue_scroll.setWidget(self.continue_page)
        self.stacked_widget.addWidget(continue_scroll)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.load_dashboard()

    def build_details_page(self):
        layout = QVBoxLayout(self.details_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(self.show_home)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

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
        
        options_layout = QHBoxLayout()
        
        # --- The Dynamic Dropdown ---
        self.season_combo = QComboBox()
        self.season_combo.currentTextChanged.connect(self.update_episode_for_season)
        
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Sub", "Dub"])
        
        self.episode_spinbox = QSpinBox()
        self.episode_spinbox.setMinimum(1)
        self.episode_spinbox.setMaximum(2000) 
        self.episode_spinbox.setFixedWidth(60)
        
        options_layout.addWidget(QLabel("<b>Season:</b>"), alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.season_combo)
        options_layout.addWidget(QLabel("<b>Audio:</b>"), alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.audio_combo)
        options_layout.addWidget(QLabel("<b>Ep:</b>"), alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.episode_spinbox)
        options_layout.addStretch() 
        
        self.play_btn = QPushButton("▶ Play Episode 1")
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedWidth(200)
        self.play_btn.clicked.connect(self.trigger_play)
        
        self.episode_spinbox.valueChanged.connect(self.update_play_button_text)

        info_layout.addWidget(self.detail_title)
        info_layout.addLayout(options_layout)
        info_layout.addWidget(self.play_btn)
        info_layout.addWidget(self.detail_synopsis)
        
        top_section.addWidget(self.detail_image)
        top_section.addLayout(info_layout)
        layout.addLayout(top_section)

    def update_play_button_text(self):
        ep = self.episode_spinbox.value()
        self.play_btn.setText(f"▶ Play Episode {ep}")

    def update_episode_for_season(self, season_name):
        """Updates the episode box if you change seasons."""
        if not season_name: return
        last_ep = get_last_watched_episode(season_name)
        
        self.episode_spinbox.blockSignals(True)
        self.episode_spinbox.setValue(last_ep)
        self.episode_spinbox.blockSignals(False)
        self.update_play_button_text()

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
        self.current_anime_data = anime_data
        self.detail_title.setText(anime_data["title"])
        self.detail_synopsis.setText("Fetching true seasons from ani-cli... (Takes 1-2 seconds)")
        
        try:
            img_data = requests.get(anime_data["image_url"]).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            self.detail_image.setPixmap(pixmap)
        except Exception:
            pass 
        
        # Switch to the details page immediately so you can see the loading text
        self.stacked_widget.setCurrentIndex(1)
        self.effect = QGraphicsOpacityEffect(self.details_page)
        self.details_page.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(400) 
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()
        
        # Force the UI to draw the "Loading" text before the script freezes
        QApplication.processEvents()
        
        # --- THE INTERCEPT: Grab the exact titles from ani-cli ---
        seasons = fetch_ani_cli_seasons(anime_data["title"])
        
        self.season_combo.blockSignals(True)
        self.season_combo.clear()
        self.season_combo.addItems(seasons)
        self.season_combo.blockSignals(False)
        
        if seasons:
            self.update_episode_for_season(seasons[0])
            
        # Put the real synopsis back
        self.detail_synopsis.setText(anime_data["synopsis"])

    def show_home(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_continue(self):
        for i in reversed(range(self.continue_layout.count())): 
            widget = self.continue_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        history = get_history()
        row, col = 0, 0
        for item in history:
            anime_data = {
                "title": item["title"],
                "image_url": item["image_url"],
                "synopsis": f"Pick up where you left off:\nEpisode {item['episode']}"
            }
            card = AnimeCard(anime_data)
            card.clicked.connect(self.open_details)
            self.continue_layout.addWidget(card, row, col)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        self.stacked_widget.setCurrentIndex(2)

    def perform_search(self):
        query = self.search_input.text()
        if not query: return
            
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
            
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
        self.show_home()

    def trigger_play(self):
        # Pass the EXACT ani-cli string that the user selected
        exact_title = self.season_combo.currentText()
        episode = self.episode_spinbox.value() 
        audio_choice = self.audio_combo.currentText()
        
        image_url = self.current_anime_data["image_url"]
        update_history(exact_title, image_url, "Season", episode)
        
        play_episode(exact_title, episode, audio_choice)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AniGui()
    window.show()
    sys.exit(app.exec())