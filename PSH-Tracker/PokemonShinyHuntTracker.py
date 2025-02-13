import tkinter as tk
from tkinter import *
from tkinter import ttk, simpledialog, colorchooser
import json
import os
from PIL import Image

class HuntTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hunt Tracker")
        self.hunts = []
        self.settings = []
        with open('./PSH-Tracker/Data/pokemonInfo.json', 'r') as file:
            self.pokemon_data = json.load(file)
        self.pokemon_names = [pokemon['name'] for pokemon in self.pokemon_data]
        self.settings_file = "./PSH-Tracker/Data/UserInfo/savedSettings.json"
        self.active_file = "./PSH-Tracker/Data/UserInfo/activeHunts.json"
        self.completed_file = "./PSH-Tracker/Data/UserInfo/completedHunts.json"
        self.create_main_window()
        self.load_settings()
        self.load_active_hunts()  # Load active hunts from file

    def create_main_window(self):
        self.add_button = tk.Button(self.root, text="Add Hunt", command=self.add_hunt)
        self.add_button.pack(pady=10)

    def add_hunt(self):
        if len(self.hunts) < 6:  # Maximum of 6 hunts
            hunt_frame = tk.Frame(self.root)
            hunt_frame.pack(pady=10, padx= 10)

            hunt_name_label = tk.Label(hunt_frame, text="Pokemon:")
            hunt_name_label.grid(row=0, column=0)

            hunt_name_entry = ttk.Combobox(hunt_frame, values=self.pokemon_names, state="normal")
            hunt_name_entry.grid(row=0, column=1)

            hunt_count_label = tk.Label(hunt_frame, text="Count:")
            hunt_count_label.grid(row=1, column=0)

            hunt_count = tk.IntVar(value=0)
            hunt_count_display = tk.Label(hunt_frame, textvariable=hunt_count)
            hunt_count_display.grid(row=1, column=1)

            def increment_count():
                hunt_count.set(hunt_count.get() + settings.increment)

            def decrement_count():
                if hunt_count.get() > 0:
                    hunt_count.set(hunt_count.get() - settings.increment)

            plus_button = tk.Button(hunt_frame, text="+", command=increment_count)
            plus_button.grid(row=1, column=2)

            minus_button = tk.Button(hunt_frame, text="-", command=decrement_count)
            minus_button.grid(row=1, column=3)

            phase_count_label = tk.Label(hunt_frame, text="Phase:")
            phase_count_label.grid(row=2, column=0)

            phase_count = tk.IntVar(value=0)
            phase_count_display = tk.Label(hunt_frame, textvariable=phase_count)
            phase_count_display.grid(row=2, column=1)

            secondary_grid = tk.Frame(hunt_frame)
            secondary_grid.grid(row=3, pady=5, padx=5)
            secondary_grid.grid_columnconfigure(5, weight=1)

            def open_secondary_window():
                self.open_hunt_window(hunt_name_entry.get(), hunt_count, settings)

            secondary_window_button = tk.Button(secondary_grid, text="Display", command=open_secondary_window)
            secondary_window_button.grid(row=3, column=0)

            complete_button = tk.Button(secondary_grid, text="Complete", command=lambda: self.complete_hunt(hunt))
            complete_button.grid(row=3, column=1)

            def increment_phase():
                phase_count.set(phase_count.get() + 1)

            phase_button = tk.Button(secondary_grid, text="Phase", command=increment_phase)
            phase_button.grid(row=3, column=2)

            settings_button = tk.Button(secondary_grid, text="Settings", command=lambda: self.open_settings(hunt, settings))
            settings_button.grid(row=3, column=3)

            clear_button = tk.Button(secondary_grid, text="Clear", command=lambda: self.clear_hunt(hunt))
            clear_button.grid(row=3, column=4)

            separator = ttk.Separator(hunt_frame, orient="horizontal")
            separator.grid(row=4, column=0, columnspan=6, sticky="ew" ,pady=10)


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

    def open_hunt_window(self, hunt_name, hunt_count_var, settings):

        index = self.pokemon_names.index(hunt_name)
        file = f"./Images/Sprites/3D/{index}.gif"
        image = Image.open(file)
        bg_color = settings.color

        frames = image.n_frames
        photoimage_obj = []
        for i in range(frames):
            obj = tk.PhotoImage(file=file, format=f"gif -index {i}")
            photoimage_obj.append(obj)

        hunt = next((h for h in self.hunts if h.name_entry.get() == hunt_name), None)

        hunt_window = tk.Toplevel(self.root)
        hunt_window.title(f"Hunt: {hunt_name}")

        if settings and hasattr(settings, 'color'):
            hunt_window.configure(bg=bg_color)

        hunt_name_label = tk.Label(hunt_window, text=f"Pokemon: {hunt_name}", bg=bg_color)
        hunt_name_label.pack(pady=10)

        image_label = tk.Label(hunt_window, image="", bg=bg_color)
        image_label.pack()

        hunt_window.image = image

        hunt_count_label = tk.Label(hunt_window, text=f"Count: {hunt_count_var.get()}", bg=bg_color)
        hunt_count_label.pack(pady=10)

        def update_count():
            hunt_count_label.config(text=f"Count: {hunt_count_var.get()}")

        hunt_count_var.trace_add("write", lambda *args: update_count())

        # close_button = tk.Button(hunt_window, text="Close", command=hunt_window.destroy)
        # close_button.pack(pady=10)

        def animate_gif(frame_index=0):

            image = photoimage_obj[frame_index]

            image_label.configure(image = image)
            frame_index += 1

            if frame_index == frames:
                frame_index = 0

            hunt_window.after(30, lambda: animate_gif(frame_index))
        
        animate_gif()

    def open_settings(self, hunt, settings):
        
        settings_window = tk.Toplevel(self.root, padx=10, pady=10)
        settings_window.title(f"Hunt Settings: {hunt.name_entry.get()}")

        increment_label = tk.Label(settings_window, text=f"Increment:")
        increment_label.grid( row=0, column= 0)

        self.increment_var = tk.IntVar(value=settings.increment)
        increment_value = tk.Label(settings_window, text=str(self.increment_var.get()))
        increment_value.grid(row=0, column=1)

        def update_increment():
            new_increment = simpledialog.askinteger(
                "Set Increment", 
                f"Enter the increment value for {hunt.name_entry.get()}:", 
                minvalue=1, 
                maxvalue=10
            )
            if new_increment is not None:
                settings.increment = new_increment  # Update settings
                self.increment_var.set(new_increment)  # Update IntVar
                increment_value.config(text=str(new_increment))

        increment_button = tk.Button(settings_window, text="Change Increment", 
                                    command=update_increment)
        increment_button.grid(row=0, column=2)

        bg_color_label = tk.Label(settings_window, text="Background Color:")
        bg_color_label.grid(row=1, column=0)

        bg_color_value = tk.Label(settings_window, text=f'{settings.color}')
        bg_color_value.grid(row=1, column=1)

        bg_color_button = tk.Button(settings_window, text="Change Color", 
                                    command=lambda: self.change_bg_color(hunt, settings))
        bg_color_button.grid(row=1, column=2)

        def save_preset():
            preset_name = simpledialog.askstring(
                "Preset Name",
                f"Enter the name for the preset:"
            )
            if preset_name is not None:
                self.save_settings(preset_name, settings)

        save_settings_button = tk.Button(settings_window, text="Save as Preset", command=save_preset)
        save_settings_button.grid(row=2, column=0)

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

    def change_increment(self, hunt, settings):
        increment_value = simpledialog.askinteger(
            "Set Increment", 
            f"Enter the increment value for {hunt.name_entry.get()}:", 
            minvalue=1, 
            maxvalue=10
        )
        if increment_value is not None:
            settings.increment = increment_value
            self.increment_var.set(increment_value)
            increment_value.con

    def change_bg_color(self, hunt, settings):
        color_code = colorchooser.askcolor(title="Choose Background Color")[1]
        if color_code:
            settings.color = color_code

    def complete_hunt(self, hunt):
        # Save hunt info to completedHunts.json
        hunt_data = {
            'name': hunt.name_entry.get(),
            'count': hunt.count_var.get(),
            'settings': hunt.settings.get(),
            'phase_counter': hunt.phase_counter.get()
        }
        # Load completed hunts
        try:
            completed_hunts = self.load_completed_hunts()

        except json.JSONDecodeError:
                    # If JSON is invalid, just start with a blank list of hunts
            pass

        # Add current hunt to completed hunts
        completed_hunts.append(hunt_data)

        # Save to completedHunts.json
        with open(self.completed_file, "w") as f:
            json.dump(completed_hunts, f, indent=4)

        # Remove hunt from active hunts
        self.hunts.remove(hunt)
        hunt.frame.destroy()

    def clear_hunt(self, hunt):
        self.hunts.remove(hunt)
        hunt.frame.destroy()

    def increment_phase(self, phase_count):
        phase_count.set(phase_count.get() + 1)
        # messagebox.showinfo("Phase Incremented", f"Phase counter for '{hunt.name_entry.get()}' is now {hunt.phase_counter}")

    def load_active_hunts(self):
        if os.path.exists(self.active_file):
            with open(self.active_file, "r") as f:
                try:
                    active_hunts = json.load(f)
                    if isinstance(active_hunts, list):
                        for hunt_data in active_hunts:
                            hunt_frame = tk.Frame(self.root)
                            hunt_frame.pack(pady=10, padx=10)

                            hunt_name_label = tk.Label(hunt_frame, text="Hunt Name:")
                            hunt_name_label.grid(row=0, column=0)

                            hunt_name_entry = ttk.Combobox(hunt_frame, values=self.pokemon_names, state="normal")
                            hunt_name_entry.insert(0, hunt_data['name'])
                            hunt_name_entry.grid(row=0, column=1)

                            
                            hunt_count_label = tk.Label(hunt_frame, text="Count:")
                            hunt_count_label.grid(row=1, column=0)

                            hunt_count = tk.IntVar(value=hunt_data['count'])
                            hunt_count_display = tk.Label(hunt_frame, textvariable=hunt_count)
                            hunt_count_display.grid(row=1, column=1)

                            def increment_count():
                                hunt_count.set(hunt_count.get() + settings.increment)

                            def decrement_count():
                                if hunt_count.get() > 0:
                                    hunt_count.set(hunt_count.get() - settings.increment)

                            plus_button = tk.Button(hunt_frame, text="+", command=increment_count)
                            plus_button.grid(row=1, column=2)

                            minus_button = tk.Button(hunt_frame, text="-", command=decrement_count)
                            minus_button.grid(row=1, column=3)

                            def open_secondary_window():
                                self.open_hunt_window(hunt_name_entry.get(), hunt_count, settings)

                            phase_count_label = tk.Label(hunt_frame, text="Phase:")
                            phase_count_label.grid(row=2, column=0)

                            phase_count = tk.IntVar(value=hunt_data['phase_counter'])
                            phase_count_display = tk.Label(hunt_frame, textvariable=phase_count)
                            phase_count_display.grid(row=2, column=1)

                            secondary_grid = tk.Frame(hunt_frame)
                            secondary_grid.grid(row=3, pady=5, padx=5)
                            secondary_grid.grid_columnconfigure(5, weight=1)

                            secondary_window_button = tk.Button(secondary_grid, text="Open Info", command=open_secondary_window)
                            secondary_window_button.grid(row=3, column=0)

                            complete_button = tk.Button(secondary_grid, text="Complete", command=lambda: self.complete_hunt(hunt))
                            complete_button.grid(row=3, column=1)

                            def increment_phase():
                                phase_count.set(phase_count.get() + 1)

                            phase_button = tk.Button(secondary_grid, text="Phase", command=increment_phase)
                            phase_button.grid(row=3, column=2)

                            settings_button = tk.Button(secondary_grid, text="Settings", command=lambda: self.open_settings(hunt, settings))
                            settings_button.grid(row=3, column=3)

                            clear_button = tk.Button(secondary_grid, text="Clear", command=lambda: self.clear_hunt(hunt))
                            clear_button.grid(row=3, column=4)

                            separator = ttk.Separator(hunt_frame, orient="horizontal")
                            separator.grid(row=4, column=0, columnspan=6, sticky="ew" ,pady=10)

                            hunt_data_obj = {
                                'frame': hunt_frame,
                                'name_entry': hunt_name_entry,
                                'count_var': hunt_count,
                                'settings': hunt_data['settings'],
                                'phase_counter': phase_count,
                            }

                            
                            hunt = type('Hunt', (), hunt_data_obj)  # Create a Hunt object for each hunt instance
                            self.hunts.append(hunt)

                            settings_data_obj = self.get_settings(hunt.settings)
                            settings = type('Settings', (), settings_data_obj)
                            self.settings.append(settings)


                except json.JSONDecodeError:
                    # If JSON is invalid, just start with a blank list of hunts
                    pass

    def load_completed_hunts(self):
        if os.path.exists(self.completed_file):
            try:
                with open(self.completed_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If the file exists but is corrupted or invalid, return an empty list
                print("Error: completedHunts.json is corrupted or invalid. Starting with an empty list.")
                return []
        return []

    def save_active_hunts(self):
        active_hunts = []
        for hunt in self.hunts:
            hunt_data = {
                'name': hunt.name_entry.get(),
                'count': hunt.count_var.get(),
                'settings': hunt.settings,
                'phase_counter': hunt.phase_counter.get(),
            }
            active_hunts.append(hunt_data)

        with open(self.active_file, "w") as f:
            json.dump(active_hunts, f, indent=4)

    def on_closing(self):
        self.save_active_hunts()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HuntTrackerApp(root)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Ensure we save active hunts on close
    root.mainloop()
