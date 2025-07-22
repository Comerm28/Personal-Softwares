import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = "WeekPlanner/events.json"

def load_events():
    if not os.path.exists("WeekPlanner"):
        os.makedirs("WeekPlanner")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_events(events):
    with open(DATA_FILE, "w") as file:
        json.dump(events, file, indent=4)

def add_event(day, events, update_calendar_callback):
    event_time = simpledialog.askstring("Add Event", "Enter the time (e.g., 10:00 AM):")
    if not event_time:
        return
    event_description = simpledialog.askstring("Add Event", "Enter the event description:")
    if not event_description:
        return
    if day not in events:
        events[day] = []
    events[day].append({"time": event_time, "description": event_description})
    save_events(events)
    update_calendar_callback()

def reset_calendar(events, update_calendar_callback):
    confirm = messagebox.askyesno("Reset Calendar", "Are you sure you want to reset the calendar?")
    if confirm:
        events.clear()
        save_events(events)
        update_calendar_callback()

def update_calendar(events, day_frames, event_color, text_color):
    for day, canvas in day_frames.items():
        canvas.delete("all")
        if day in events:
            for i, event in enumerate(events[day]):
                y1 = i * 50
                y2 = y1 + 40
                canvas.create_rectangle(10, y1 + 10, 190, y2 + 10, fill=event_color, outline="")
                canvas.create_text(20, y1 + 30, anchor="w", text=f"{event['time']} - {event['description']}", fill=text_color, font=("Arial", 10))

class WeekPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Week Planner")
        self.root.geometry("1000x600")
        self.bg_color = "#2d2d2d"
        self.event_color = "#3d3d3d"
        self.text_color = "#ffffff"
        self.accent_color = "#5c6bc0"
        self.highlight_color = "#7986cb"
        self.days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.events = load_events()
        self.day_frames = {}
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.header_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.header_frame.pack(fill=tk.X)

        self.reset_button = tk.Button(
            self.header_frame,
            text="Reset Calendar",
            command=lambda: reset_calendar(self.events, self.update_calendar),
            bg=self.accent_color,
            fg="white",
            activebackground=self.highlight_color,
            activeforeground="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        self.reset_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.calendar_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for i, day in enumerate(self.days):
            day_frame = tk.Frame(self.calendar_frame, bg=self.bg_color, relief=tk.RAISED, bd=1)
            day_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            self.calendar_frame.columnconfigure(i, weight=1)

            day_label = tk.Label(day_frame, text=day, bg=self.accent_color, fg="white", font=("Arial", 12, "bold"))
            day_label.pack(fill=tk.X)

            add_event_button = tk.Button(
                day_frame,
                text="Add Event",
                command=lambda d=day: add_event(d, self.events, self.update_calendar),
                bg=self.accent_color,
                fg="white",
                activebackground=self.highlight_color,
                activeforeground="white",
                font=("Arial", 10),
                relief=tk.FLAT
            )
            add_event_button.pack(fill=tk.X, pady=5)

            event_canvas = tk.Canvas(day_frame, bg=self.event_color, highlightthickness=0)
            event_canvas.pack(fill=tk.BOTH, expand=True)
            self.day_frames[day] = event_canvas

        self.update_calendar()

    def update_calendar(self):
        update_calendar(self.events, self.day_frames, self.accent_color, self.text_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeekPlannerApp(root)
    root.mainloop()