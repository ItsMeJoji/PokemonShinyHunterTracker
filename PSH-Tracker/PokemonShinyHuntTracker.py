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
            #secondary_window_button.clicked.connect(lambda: self.open_hunt_window(hunt_name_entry.currentText(), hunt_count))
            secondary_window_button.clicked.connect(lambda: self.open_hunt_window(hunt, hunt_count))
            hunt_layout.addWidget(secondary_window_button)

            complete_button = QPushButton("Complete", hunt_frame)
            complete_button.clicked.connect(lambda: self.complete_hunt(hunt))
            hunt_layout.addWidget(complete_button)

            phase_button = QPushButton("Phase", hunt_frame)
            phase_button.clicked.connect(lambda: phase_count.setValue(phase_count.value() + 1))
            phase_button.clicked.connect(lambda: hunt_count.setValue(0))
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
            if hunt_data["settings"]:
                settings_data = self.get_settings(hunt_data["settings"])
            else:
                settings_data = {
                    'name': "default",
                    'color': "#c0c0c0",
                    'increment': 1
                }
            hunt = type('Hunt', (), hunt_data)  # Create a Hunt object for each hunt instance
            self.hunts.append(hunt)
            settings = type('Settings', (), settings_data)
            self.settings.append(settings)

    def open_hunt_window(self, hunt, hunt_count_var):
        hunt_name = hunt.name_entry.currentText()
        index = self.pokemon_names.index(hunt_name)
        file = f"./PSH-Tracker/Images/Sprites/3D/{index}.gif"
        image = QMovie(file)
        settings = self.get_settings(hunt.settings)  # Get settings for the hunt
        bg_color = "#c0c0c0"  # Default background color
        bg_color = settings.get('color', bg_color) if settings else bg_color

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
        hunt_count_label.move(10, 400)

        hunt_window.show()

    def open_settings(self, hunt, settings):

        settings_window = QDialog(self)
        settings_window.setWindowTitle(f"Hunt Settings: {hunt.name_entry.currentText()}")

        #load all settings from file
        all_settings = self.load_settings()

        #Settings Dropdown
        settings_dropdown = QComboBox(settings_window)
        settings_dropdown.move(10, 0)
        settings_names = ["default"] + [s["name"] for s in all_settings if s["name"] != "default"]
        settings_dropdown.addItems(settings_names)
        current_index = settings_names.index(hunt.settings) if hunt.settings in settings_names else 0
        settings_dropdown.setCurrentIndex(current_index)

        # Get the settings data for the current selection
        def get_selected_settings():
            selected_name = settings_dropdown.currentText()
            return self.get_settings(selected_name) or {'name': 'default', 'color': '#c0c0c0', 'increment': 1}

        # Update fields when dropdown changes
        def update_fields():
            selected_settings = get_selected_settings()
            increment_value.setText(str(selected_settings['increment']))
            bg_color_value.setText(selected_settings['color'])
            bg_color_value.setStyleSheet(f"background-color: {selected_settings['color']}; padding: 2px;")
        settings_dropdown.currentIndexChanged.connect(update_fields)


        #Settings Increment
        settings_data = self.get_settings(hunt.settings)
        increment_label = QLabel("Increment:", settings_window)
        increment_label.move(10, 30)

        increment_value = QLabel(str(settings_data['increment']), settings_window)
        increment_value.move(100, 30)

        increment_button = QPushButton("Change Increment", settings_window)
        increment_button.move(200, 30)
        increment_button.clicked.connect(lambda: self.change_increment(hunt, get_selected_settings(), increment_value))

        #Settings Background Color
        bg_color_label = QLabel("Background Color:", settings_window)
        bg_color_label.move(10, 60)

        bg_color_value = QLabel(settings_data['color'], settings_window)
        bg_color_value.move(150, 60)
        bg_color_value.setStyleSheet(f"background-color: {settings_data['color']}; padding: 2px;")

        bg_color_button = QPushButton("Change Color", settings_window)
        bg_color_button.move(250, 60)
        bg_color_button.clicked.connect(lambda: self.change_bg_color(get_selected_settings(), bg_color_value))

        okay_button = QPushButton("Close", settings_window)
        okay_button.move(10,90)
        okay_button.clicked.connect(settings_window.accept)

        def get_current_settings():
            return {
                'name': settings_dropdown.currentText(),
                'color': bg_color_value.text(),
                'increment': int(increment_value.text())
            }

        update_settings_button = QPushButton("Update Current Settings", settings_window)
        update_settings_button.move(150, 90)
        update_settings_button.clicked.connect(lambda: self.save_settings(settings_dropdown.currentText(), get_current_settings()))

        save_settings_button = QPushButton("Save as New Settings", settings_window)
        save_settings_button.move(300, 90)

        def save_as_new_settings():
            text, ok = QInputDialog.getText(settings_window, "Save Settings As", "Enter a name for the new settings:")
            if ok and text:
                # Use the entered name as the first argument
                current_settings = get_current_settings()
                current_settings['name'] = text  # Update the name in the settings dict
                self.save_settings(text, current_settings)
                settings_names.append(text)  # Add the new name to the dropdown
                settings_dropdown.addItem(text)  # Add the new name to the dropdown
                settings_dropdown.setCurrentText(text)
        save_settings_button.clicked.connect(save_as_new_settings)


        settings_window.show()

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as file:
                return json.load(file)
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
        all_settings = self.load_settings()
        new_settings = {
            'name': name,
            'color': settings['color'],
            'increment': settings['increment']
        }
        try:
            all_settings.remove(self.get_settings(name))  # Remove existing settings with the same name
        except (ValueError, TypeError):
            pass
        all_settings.append(new_settings)
        with open(self.settings_file, "w") as file:
            json.dump(all_settings, file, indent=4)

    def change_increment(self, hunt, settings, increment_label):
        increment_value, ok = QInputDialog.getInt(self, "Set Increment", f"Enter the increment value for {hunt.name_entry.currentText()}:", min=1, max=10)
        if ok:
            settings['increment'] = increment_value
            increment_label.setText(str(increment_value))

    def change_bg_color(self, settings, bg_color_value):
        color_code = QColorDialog.getColor().name()
        if color_code:
            settings['color'] = color_code
            bg_color_value.setText(color_code)
            bg_color_value.setStyleSheet(f"background-color: {color_code}; padding: 4px;")

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