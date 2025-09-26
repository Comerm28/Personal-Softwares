import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
from datetime import datetime

class GymDashApp:
    def __init__(self, root):
        # Initialize the Gym Dashboard app
        self.root = root
        self.root.title("Gym Dashboard")
        self.root.geometry("800x600")
        
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#ff6b35"
        self.highlight_color = "#ff8c69"
        
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", 
                            background="#444444", 
                            foreground="#ffffff",
                            padding=[10, 2],
                            font=("Arial", 10))

        self.style.map("TNotebook.Tab", 
                      background=[("selected", self.accent_color), ("!selected", "#444444")],
                      foreground=[("selected", "#ffffff"), ("!selected", "#ffffff")])
        
        self.muscle_groups = ["Legs", "Chest", "Biceps", "Back", "Triceps", "Shoulders", "Abs"]
        self.workouts = self.load_workouts()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create the main UI layout with tabs
        self.tab_control = ttk.Notebook(self.root)
        
        self.workout_tab = ttk.Frame(self.tab_control)
        self.stats_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.workout_tab, text='Log Workout')
        self.tab_control.add(self.stats_tab, text='Statistics')
        
        self.tab_control.pack(expand=1, fill='both')
        
        self.create_workout_tab()
        self.create_stats_tab()
        
    def create_workout_tab(self):
        # Create the workout logging tab
        self.workout_tab.columnconfigure(0, weight=1)
        self.workout_tab.rowconfigure(3, weight=1)
        
        title_label = tk.Label(self.workout_tab, text="Log Your Workout", font=("Arial", 14, "bold"),
                              bg=self.bg_color, fg=self.text_fg)
        title_label.grid(row=0, column=0, pady=(10, 20))
        
        input_frame = tk.Frame(self.workout_tab, bg=self.bg_color)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        
        tk.Label(input_frame, text="Exercise Name:", bg=self.bg_color, fg=self.text_fg,
                font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        self.exercise_entry = tk.Entry(input_frame, bg=self.text_bg, fg=self.text_fg,
                                     insertbackground=self.text_fg, font=("Arial", 11))
        self.exercise_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        tk.Label(input_frame, text="Reps:", bg=self.bg_color, fg=self.text_fg,
                font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        
        self.reps_entry = tk.Entry(input_frame, bg=self.text_bg, fg=self.text_fg,
                                 insertbackground=self.text_fg, font=("Arial", 11))
        self.reps_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        tk.Label(input_frame, text="Muscle Group:", bg=self.bg_color, fg=self.text_fg,
                font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        
        self.muscle_var = tk.StringVar()
        self.muscle_dropdown = ttk.Combobox(input_frame, textvariable=self.muscle_var,
                                          values=self.muscle_groups, state="readonly")
        self.muscle_dropdown.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        tk.Label(input_frame, text="Intensity (1-10):", bg=self.bg_color, fg=self.text_fg,
                font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        
        self.intensity_var = tk.IntVar()
        self.intensity_scale = tk.Scale(input_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                      variable=self.intensity_var, bg=self.bg_color,
                                      fg=self.text_fg, highlightthickness=0,
                                      troughcolor=self.text_bg, activebackground=self.accent_color)
        self.intensity_scale.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        button_frame = tk.Frame(self.workout_tab, bg=self.bg_color)
        button_frame.grid(row=2, column=0, pady=20)
        
        self.log_button = tk.Button(button_frame, text="Log Exercise", command=self.log_exercise,
                                  bg=self.accent_color, fg="white", activebackground=self.highlight_color,
                                  activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                  padx=15, pady=8)
        self.log_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="Clear Form", command=self.clear_form,
                                    bg="#666666", fg="white", activebackground="#888888",
                                    activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                    padx=15, pady=8)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        history_label = tk.Label(self.workout_tab, text="Recent Workouts", font=("Arial", 12, "bold"),
                               bg=self.bg_color, fg=self.text_fg)
        history_label.grid(row=3, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.workout_listbox = tk.Listbox(self.workout_tab, bg=self.text_bg, fg=self.text_fg,
                                        selectbackground=self.accent_color, selectforeground="white",
                                        font=("Arial", 10))
        self.workout_listbox.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.load_workout_list()
        
    def create_stats_tab(self):
        # Create the statistics tab
        self.stats_tab.columnconfigure(0, weight=1)
        self.stats_tab.rowconfigure(1, weight=1)
        
        title_label = tk.Label(self.stats_tab, text="Workout Statistics", font=("Arial", 14, "bold"),
                              bg=self.bg_color, fg=self.text_fg)
        title_label.grid(row=0, column=0, pady=(20, 30))
        
        stats_frame = tk.Frame(self.stats_tab, bg=self.bg_color)
        stats_frame.grid(row=1, column=0, padx=20, sticky="nsew")
        stats_frame.columnconfigure(0, weight=1)
        
        self.stats_text = tk.Text(stats_frame, bg=self.text_bg, fg=self.text_fg,
                                font=("Arial", 11), wrap=tk.WORD, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        refresh_button = tk.Button(self.stats_tab, text="Refresh Stats", command=self.update_stats,
                                 bg=self.accent_color, fg="white", activebackground=self.highlight_color,
                                 activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                 padx=15, pady=8)
        refresh_button.grid(row=2, column=0, pady=20)
        
        self.update_stats()
        
    def log_exercise(self):
        # Log a new exercise entry
        exercise_name = self.exercise_entry.get().strip()
        reps = self.reps_entry.get().strip()
        muscle_group = self.muscle_var.get()
        intensity = self.intensity_var.get()
        
        if not exercise_name:
            messagebox.showwarning("Warning", "Exercise name cannot be empty!")
            return
            
        if not reps or not reps.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid number of reps!")
            return
            
        if not muscle_group:
            messagebox.showwarning("Warning", "Please select a muscle group!")
            return
        
        workout_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercise": exercise_name,
            "reps": int(reps),
            "muscle_group": muscle_group,
            "intensity": intensity
        }
        
        self.workouts.append(workout_entry)
        self.save_workouts()
        self.clear_form()
        self.load_workout_list()
        self.update_stats()
        messagebox.showinfo("Success", "Exercise logged successfully!")
    
    def clear_form(self):
        # Clear all input fields
        self.exercise_entry.delete(0, tk.END)
        self.reps_entry.delete(0, tk.END)
        self.muscle_var.set("")
        self.intensity_var.set(5)
    
    def load_workouts(self):
        # Load workout data from JSON file
        try:
            if not os.path.exists("GymDashboard"):
                os.makedirs("GymDashboard")
                
            if os.path.exists("GymDashboard/info.json"):
                with open("GymDashboardinfo.json", "r") as file:
                    return json.load(file)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load workouts: {str(e)}")
            return []
    
    def save_workouts(self):
        # Save workout data to JSON file
        try:
            if not os.path.exists("GymDashboard"):
                os.makedirs("GymDashboard")
                
            with open("GymDashboard/info.json", "w") as file:
                json.dump(self.workouts, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save workouts: {str(e)}")
    
    def load_workout_list(self):
        # Load recent workouts into the listbox
        self.workout_listbox.delete(0, tk.END)
        
        sorted_workouts = sorted(self.workouts, key=lambda x: x['date'], reverse=True)
        
        for workout in sorted_workouts[:10]:
            display_text = f"{workout['date'][:10]} - {workout['exercise']} ({workout['muscle_group']}) - {workout['reps']} reps"
            self.workout_listbox.insert(tk.END, display_text)
    
    def update_stats(self):
        # Update the statistics display
        if not self.workouts:
            stats_text = "No workout data available yet.\nStart logging your exercises to see statistics!"
        else:
            total_workouts = len(self.workouts)
            total_reps = sum(workout['reps'] for workout in self.workouts)
            avg_intensity = sum(workout['intensity'] for workout in self.workouts) / total_workouts
            
            muscle_counts = {}
            for workout in self.workouts:
                muscle = workout['muscle_group']
                muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
            
            most_worked = max(muscle_counts, key=muscle_counts.get) if muscle_counts else "None"
            
            recent_workouts = len([w for w in self.workouts 
                                 if datetime.strptime(w['date'], "%Y-%m-%d %H:%M:%S").date() >= 
                                 (datetime.now().date() - datetime.timedelta(days=7))])
            
            stats_text = f"""WORKOUT STATISTICS
====================

Total Exercises Logged: {total_workouts}
Total Reps Completed: {total_reps:,}
Average Intensity: {avg_intensity:.1f}/10

Most Worked Muscle Group: {most_worked}
Workouts This Week: {recent_workouts}

MUSCLE GROUP BREAKDOWN:
{'-' * 25}
"""
            
            for muscle, count in sorted(muscle_counts.items()):
                percentage = (count / total_workouts) * 100
                stats_text += f"{muscle}: {count} exercises ({percentage:.1f}%)\n"
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = GymDashApp(root)
    root.mainloop()