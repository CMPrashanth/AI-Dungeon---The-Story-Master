import sys
import os
import re
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSlider
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QUrl, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class StoryWorker(QThread):
    # Emits the full story (with modulation cues) and a cleaned version (for display)
    story_generated = pyqtSignal(str, str)
    status_update = pyqtSignal(str)

    def __init__(self, premise):
        super().__init__()
        self.premise = premise

    def run(self):
        from story_generator import enhance_prompt, generate_text as generate_story
        enhanced_prompt = enhance_prompt(self.premise)
        full_story = generate_story(enhanced_prompt)
        display_story = re.sub(r'\[[^\]]*\]', '', full_story)
        self.story_generated.emit(full_story, display_story)
        self.status_update.emit("Story generated.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Dungeon Master")
        self.resize(1000, 800)
        self.narrator = None
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.setup_ui()
        # Timer to update the progress slider every 500 ms.
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_position)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Premise Input Area ---
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your story premise...")
        self.input_field.setFont(QFont("Segoe UI", 12))
        input_layout.addWidget(QLabel("Premise:"))
        input_layout.addWidget(self.input_field)
        self.generate_button = QPushButton("Generate Story")
        self.generate_button.clicked.connect(self.on_generate_story)
        input_layout.addWidget(self.generate_button)
        main_layout.addLayout(input_layout)
        
        # --- Story Display Area ---
        self.story_display = QTextEdit()
        self.story_display.setReadOnly(True)
        self.story_display.setFont(QFont("Segoe UI", 12))
        main_layout.addWidget(self.story_display)
        
        # --- Audio Player Controls Area ---
        player_layout = QVBoxLayout()
        # Position/Progress slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        player_layout.addWidget(self.position_slider)
        
        # Controls: Play/Pause, Backward, Forward, Reset, and Speed Control
        controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.on_play_pause)
        controls_layout.addWidget(self.play_pause_button)
        
        self.backward_button = QPushButton("<<")
        self.backward_button.clicked.connect(self.on_backward)
        controls_layout.addWidget(self.backward_button)
        
        self.forward_button = QPushButton(">>")
        self.forward_button.clicked.connect(self.on_forward)
        controls_layout.addWidget(self.forward_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.on_reset)
        controls_layout.addWidget(self.reset_button)
        
        # Playback speed slider and label
        self.speed_label = QLabel("Speed: 1.0x")
        controls_layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)   # 0.5x
        self.speed_slider.setMaximum(200)  # 2.0x
        self.speed_slider.setValue(100)      # 1.0x default
        self.speed_slider.setTickInterval(10)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.sliderReleased.connect(self.on_speed_change)
        controls_layout.addWidget(self.speed_slider)
        
        player_layout.addLayout(controls_layout)
        main_layout.addLayout(player_layout)
        
        # --- Status Label ---
        self.status_label = QLabel("Awaiting input...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(self.status_label)
        
        # --- Modern Styling via QSS ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1E1E2F; }
            QLabel { color: #C7C7C7; font-size: 14px; }
            QLineEdit { background-color: #2E2E3E; color: #FFFFFF; padding: 6px; border: 1px solid #4B4B6B; border-radius: 4px; }
            QPushButton { background-color: #3E64FF; color: #FFFFFF; border: none; border-radius: 4px; padding: 8px 16px; }
            QPushButton:hover { background-color: #5E84FF; }
            QTextEdit { background-color: #2E2E3E; color: #FFFFFF; padding: 10px; border: 1px solid #4B4B6B; border-radius: 4px; }
            QSlider::groove:horizontal { border: 1px solid #4B4B6B; height: 8px; background: #3E3E50; margin: 0px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #3E64FF; border: 1px solid #4B4B6B; width: 18px; margin: -4px 0; border-radius: 9px; }
        """)
        
        # Connect QMediaPlayer signals to update the position slider.
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        
    def on_generate_story(self):
        premise = self.input_field.text().strip()
        if premise.lower() == "quit":
            QApplication.quit()
            sys.exit(0)
        self.generate_button.setEnabled(False)
        self.status_label.setText("Generating story...")
        self.worker = StoryWorker(premise)
        self.worker.story_generated.connect(self.on_story_generated)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()
        
    def on_story_generated(self, full_text, display_text):
        self.story_display.setPlainText(display_text)
        self.status_label.setText("Story generated. Preparing narration...")
        
        from voice_generator import VoiceNarrator
        self.narrator = VoiceNarrator()
        
        # ✅ Extract the correct file path from the tuple
        audio_file, _ = self.narrator.save_to_temp_file(full_text)

        # Ensure the file exists before playing
        if not os.path.exists(audio_file):
            self.status_label.setText("❌ Error: Audio file not found!")
            return
        
        self.status_label.setText("Narration ready. Playing audio...")
        self.player.setSource(QUrl.fromLocalFile(audio_file))  # ✅ Now correctly a string
        self.player.play()
        self.play_pause_button.setText("Pause")
        self.timer.start()
        
    def update_status(self, status):
        self.status_label.setText(status)
        
    def on_worker_finished(self):
        self.generate_button.setEnabled(True)
        
    def on_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_pause_button.setText("Play")
            self.status_label.setText("Paused.")
        else:
            self.player.play()
            self.play_pause_button.setText("Pause")
            self.status_label.setText("Playing...")
            
    def on_forward(self):
        # Skip forward 5 seconds (5000 ms)
        new_pos = self.player.position() + 5000
        self.player.setPosition(new_pos)
        self.status_label.setText("Forwarded 5 seconds.")
        
    def on_backward(self):
        new_pos = max(0, self.player.position() - 5000)
        self.player.setPosition(new_pos)
        self.status_label.setText("Rewinded 5 seconds.")
        
    def on_speed_change(self):
        # Map slider value (50 to 200) to playback rate (0.5x to 2.0x)
        speed = self.speed_slider.value() / 100.0
        self.player.setPlaybackRate(speed)
        self.speed_label.setText(f"Speed: {speed:.1f}x")
        
    def on_reset(self):
        # Reset input, story display, audio playback, and status.
        self.input_field.clear()
        self.story_display.clear()
        self.player.stop()
        self.play_pause_button.setText("Play")
        self.speed_slider.setValue(100)
        self.status_label.setText("Reset complete. Awaiting input...")
        
    def position_changed(self, position):
        self.position_slider.setValue(position)
        
    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        
    def update_position(self):
        self.position_slider.setValue(self.player.position())
        
    def set_position(self, position):
        self.player.setPosition(position)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
