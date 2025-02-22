import sys
import json
import os
import keyboard
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox, QSpinBox, QDialog, QColorDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QMovie, QKeySequence, QShortcut
from PyQt6.QtCore import Qt
from counter_handler import IncrementCount, DecrementCount

class HuntTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hunt Tracker")
        self.hunts = []
        self.settings = []
        with open('./PSH-Tracker/Data/pokemonInfo.json', 'r') as file:
            self.pokemon_data = json.load(file)
        self.pokemon_names = [pokemon['name'] for pokemon in self.pokemon_data]
        self.settings_file = "./PSH-Tracker/Data/UserInfo/savedSettings.json"
        self.active_file = "./PSH-Tracker/Data/UserInfo/activeHunts.json"
        self.completed_file = "./PSH-Tracker/Data/UserInfo/completedHunts.json"
        self.initUI()
        self.load_settings()
        self.load_active_hunts()  # Load active hunts from file

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.add_button = QPushButton("Add Hunt", self)
        self.add_button.clicked.connect(self.add_hunt)
        self.layout.addWidget(self.add_button)

    def add_hunt(self):
        if len(self.hunts) < 6:  # Maximum of 6 hunts
            hunt_frame = QWidget(self)
            hunt_layout = QVBoxLayout(hunt_frame)

            #Hunt Info

            hunt_name_label = QLabel("Pokemon:", hunt_frame)
            hunt_layout.addWidget(hunt_name_label)

            hunt_name_entry = QComboBox(hunt_frame)
            hunt_name_entry.addItems(self.pokemon_names)
            hunt_layout.addWidget(hunt_name_entry)

            hunt_count_label = QLabel("Count:", hunt_frame)
            hunt_layout.addWidget(hunt_count_label)

            hunt_count = QSpinBox(hunt_frame)
            hunt_count.setValue(0)
            hunt_layout.addWidget(hunt_count)

            # Increment and Decrement Buttons

            increment_button = QPushButton("+", hunt_frame)
            increment_button.clicked.connect(lambda: hunt_count.setValue(IncrementCount(hunt_count.value(), settings.increment)))
            hunt_layout.addWidget(increment_button)

            decrement_button = QPushButton("-", hunt_frame)
            decrement_button.clicked.connect(lambda: hunt_count.setValue(DecrementCount(hunt_count.value(), settings.increment) if hunt_count.value() > 0 else 0))
            hunt_layout.addWidget(decrement_button)

            increment_shortcut = QShortcut(QKeySequence("+"), self)
            increment_shortcut.activated.connect(lambda: hunt_count.setValue(IncrementCount(hunt_count.value(), settings.increment)))
            increment_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

            decrement_shortcut = QShortcut(QKeySequence("-"), self)
            decrement_shortcut.activated.connect(lambda: hunt_count.setValue(DecrementCount(hunt_count.value(), settings.increment) if hunt_count.value() > 0 else 0))
            decrement_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

            # Phase Counter

            phase_count_label = QLabel("Phase:", hunt_frame)
            hunt_layout.addWidget(phase_count_label)

            phase_count = QSpinBox(hunt_frame)
            phase_count.setValue(0)
            hunt_layout.addWidget(phase_count)

            # Various Buttons

            secondary_window_button = QPushButton("Display", hunt_frame)
            secondary_window_button.clicked.connect(lambda: self.open_hunt_window(hunt_name_entry.currentText(), hunt_count))
            hunt_layout.addWidget(secondary_window_button)

            complete_button = QPushButton("Complete", hunt_frame)
            complete_button.clicked.connect(lambda: self.complete_hunt(hunt))
            hunt_layout.addWidget(complete_button)

            phase_button = QPushButton("Phase", hunt_frame)
            phase_button.clicked.connect(lambda: phase_count.setValue(phase_count.value() + 1))
            hunt_layout.addWidget(phase_button)

            settings_button = QPushButton("Settings", hunt_frame)
            settings_button.clicked.connect(lambda: self.open_settings(hunt, settings))
            hunt_layout.addWidget(settings_button)

            clear_button = QPushButton("Clear", hunt_frame)
            clear_button.clicked.connect(lambda: self.clear_hunt(hunt))
            hunt_layout.addWidget(clear_button)

            hunt_frame.setLayout(hunt_layout)
            self.layout.addWidget(hunt_frame)

            hunt_data = {
                'frame': hunt_frame,
                'name_entry': hunt_name_entry,
                'count_var': hunt_count,
                'settings': "default",  # Default increment for each hunt
                'phase_counter': phase_count,  # Phase counter initialized to 0
            }
            settings_data = {
                'name': "default",
                'color': "#c0c0c0",
                'increment': 1
            }
            hunt = type('Hunt', (), hunt_data)  # Create a Hunt object for each hunt instance
            self.hunts.append(hunt)
            settings = type('Settings', (), settings_data)
            self.settings.append(settings)

    def open_hunt_window(self, hunt_name, hunt_count_var):
        index = self.pokemon_names.index(hunt_name)
        file = f"./PSH-Tracker/Images/Sprites/3D/{index}.gif"
        image = QMovie(file)
        bg_color = "#c0c0c0"

        hunt_window = QDialog(self)
        hunt_window.setWindowTitle(f"Hunt: {hunt_name}")
        hunt_window.setStyleSheet(f"background-color: {bg_color};")

        hunt_name_label = QLabel(f"Pokemon: {hunt_name}", hunt_window)
        hunt_name_label.setStyleSheet(f"background-color: {bg_color};")
        hunt_name_label.move(10, 10)

        image_label = QLabel(hunt_window)
        movie = image
        image_label.setMovie(movie)
        movie.start()
        image_label.move(10, 50)

        hunt_count_label = QLabel(f"Count: {hunt_count_var.value()}", hunt_window)
        hunt_count_label.setStyleSheet(f"background-color: {bg_color};")
        hunt_count_label.move(10, 200)

        hunt_window.exec()

    def open_settings(self, hunt, settings):
        settings_window = QDialog(self)
        settings_window.setWindowTitle(f"Hunt Settings: {hunt.name_entry.currentText()}")

        increment_label = QLabel("Increment:", settings_window)
        increment_label.move(10, 10)

        increment_value = QLabel(str(settings.increment), settings_window)
        increment_value.move(100, 10)

        increment_button = QPushButton("Change Increment", settings_window)
        increment_button.move(200, 10)
        increment_button.clicked.connect(lambda: self.change_increment(hunt, settings, increment_value))

        bg_color_label = QLabel("Background Color:", settings_window)
        bg_color_label.move(10, 50)

        bg_color_value = QLabel(settings.color, settings_window)
        bg_color_value.move(150, 50)

        bg_color_button = QPushButton("Change Color", settings_window)
        bg_color_button.move(250, 50)
        bg_color_button.clicked.connect(lambda: self.change_bg_color(hunt))

        okay_button = QPushButton("Okay", settings_window)
        okay_button.move(10,90)
        okay_button.clicked.connect(settings_window.accept)

        save_settings_button = QPushButton("Save as Preset", settings_window)
        save_settings_button.move(150, 90)
        save_settings_button.clicked.connect(lambda: self.save_settings(hunt.settings.name, hunt.settings))

        settings_window.exec()

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as file:
                self.settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {}

    def get_settings(self, name):
        with open(self.settings_file, "r") as file:
            settings_list = json.load(file)

        for settings in settings_list:
            if settings.get("name") == name:
                return settings
        return

    def save_settings(self, name, settings):
        with open(self.settings_file, "w") as file:
            settings.name = name
            json.dump(self.settings, file, indent=4)

    def change_increment(self, hunt, settings, increment_label):
        increment_value, ok = QInputDialog.getInt(self, "Set Increment", f"Enter the increment value for {hunt.name_entry.currentText()}:", min=1, max=10)
        if ok:
            settings.increment = increment_value
            increment_label.setText(str(increment_value))

    def change_bg_color(self, hunt):
        color_code = QColorDialog.getColor().name()
        if color_code:
            hunt.settings.color = color_code

    def complete_hunt(self, hunt):
        hunt_data = {
            'name': hunt.name_entry.currentText(),
            'count': hunt.count_var.value(),
            'settings': hunt.settings,
            'phase_counter': hunt.phase_counter.value()
        }
        try:
            completed_hunts = self.load_completed_hunts()
        except json.JSONDecodeError:
            completed_hunts = []

        completed_hunts.append(hunt_data)

        with open(self.completed_file, "w") as f:
            json.dump(completed_hunts, f, indent=4)

        self.hunts.remove(hunt)
        hunt.frame.deleteLater()

    def clear_hunt(self, hunt):
        self.hunts.remove(hunt)
        hunt.frame.deleteLater()

    def load_active_hunts(self):
        if os.path.exists(self.active_file):
            with open(self.active_file, "r") as f:
                try:
                    active_hunts = json.load(f)
                    if isinstance(active_hunts, list):
                        for hunt_data in active_hunts:
                            self.add_hunt()
                            hunt = self.hunts[-1]
                            hunt.name_entry.setCurrentText(hunt_data['name'])
                            hunt.count_var.setValue(hunt_data['count'])
                            hunt.phase_counter.setValue(hunt_data['phase_counter'])
                            hunt.settings = hunt_data['settings']
                except json.JSONDecodeError:
                    pass

    def load_completed_hunts(self):
        if os.path.exists(self.completed_file):
            try:
                with open(self.completed_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_active_hunts(self):
        active_hunts = []
        for hunt in self.hunts:
            hunt_data = {
                'name': hunt.name_entry.currentText(),
                'count': hunt.count_var.value(),
                'settings': hunt.settings,
                'phase_counter': hunt.phase_counter.value(),
            }
            active_hunts.append(hunt_data)

        with open(self.active_file, "w") as f:
            json.dump(active_hunts, f, indent=4)

    def closeEvent(self, event):
        self.save_active_hunts()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HuntTrackerApp()
    window.show()
    sys.exit(app.exec())