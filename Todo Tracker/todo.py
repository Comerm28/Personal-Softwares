import json
import os
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

DATA_FILE = "Todo Tracker/todo_data.txt"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
            if "tasks" in data:
                for task_name, task_data in data["tasks"].items():
                    if "notes" not in task_data:
                        task_data["notes"] = ""
            
            if "lifetime_goals" not in data:
                data["lifetime_goals"] = {}
                
            return data
    return {
        "tasks": {}, 
        "four_month_goals": {},
        "five_year_goals": {},
        "lifetime_goals": {},
        "last_reset": str(date.today())
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_task():
    task = simpledialog.askstring("Add Task", "Enter task name:")
    if task and task not in data["tasks"]:
        recurring = messagebox.askyesno("Recurring Task", "Should this task recur daily?")
        notes = simpledialog.askstring("Task Notes", "Add notes for this task (optional):", initialvalue="")
        
        data["tasks"][task] = {
            "completions": [],
            "recurring": recurring,
            "notes": notes if notes else ""
        }
        update_list()
        save_data(data)

def mark_completed():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        task_name = selected_task.split(" - ")[0]
        if "(" in task_name:
            task_name = task_name.split(" (")[0]
        
        today = str(date.today())
        if today not in data["tasks"][task_name]["completions"]:
            data["tasks"][task_name]["completions"].append(today)
            update_list()
            save_data(data)
        else:
            messagebox.showinfo("Info", f"'{task_name}' already completed today.")

def delete_task():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        task_name = selected_task.split(" - ")[0]
        if "(" in task_name:
            task_name = task_name.split(" (")[0]
        if "📝" in task_name:
            task_name = task_name.split(" 📝")[0]
            
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task_name}'?")
        if confirm:
            del data["tasks"][task_name]
            update_list()
            save_data(data)
            messagebox.showinfo("Success", f"Task '{task_name}' deleted.")

def edit_task():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        old_task_name = selected_task.split(" - ")[0]
        if "(" in old_task_name:
            old_task_name = old_task_name.split(" (")[0]
            
        new_task_name = simpledialog.askstring("Edit Task", "Enter new task name:", initialvalue=old_task_name)
        
        if new_task_name and new_task_name != old_task_name:
            if new_task_name in data["tasks"]:
                messagebox.showerror("Error", f"Task '{new_task_name}' already exists.")
                return
                
            data["tasks"][new_task_name] = data["tasks"][old_task_name]
            del data["tasks"][old_task_name]
            
            update_list()
            save_data(data)
            messagebox.showinfo("Success", f"Task renamed to '{new_task_name}'")

def toggle_recurring():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        task_name = selected_task.split(" - ")[0]
        if "(" in task_name:
            task_name = task_name.split(" (")[0]
            
        current_state = data["tasks"][task_name]["recurring"]
        data["tasks"][task_name]["recurring"] = not current_state
        new_state = "recurring" if data["tasks"][task_name]["recurring"] else "non-recurring"
        update_list()
        save_data(data)
        messagebox.showinfo("Task Updated", f"'{task_name}' is now {new_state}.")

def check_daily_reset():
    today = str(date.today())
    if "last_reset" not in data or data["last_reset"] != today:
        non_recurring_tasks = [task for task, info in data["tasks"].items() 
                               if not info["recurring"]]
        
        for task in non_recurring_tasks:
            if data["tasks"][task]["completions"]:
                latest_completion = data["tasks"][task]["completions"][-1]
                latest_date = datetime.strptime(latest_completion, "%Y-%m-%d").date()
                yesterday = date.today() - timedelta(days=1)
                if latest_date <= yesterday:
                    del data["tasks"][task]
        
        data["last_reset"] = today
        update_list()
        save_data(data)
        return True
    return False

def update_list():
    task_listbox.delete(0, tk.END)
    for task, info in data["tasks"].items():
        recurring_marker = " (recurring)" if info["recurring"] else ""
        notes_marker = " 📝" if info.get("notes", "") else ""
        completions = len(info["completions"])
        task_listbox.insert(tk.END, f"{task}{recurring_marker}{notes_marker} - {completions} days completed")

def edit_notes():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        task_name = selected_task.split(" - ")[0]
        if "(" in task_name:
            task_name = task_name.split(" (")[0]
            
        current_notes = data["tasks"][task_name].get("notes", "")
        
        new_notes = simpledialog.askstring("Edit Notes", 
                                         f"Notes for '{task_name}':",
                                         initialvalue=current_notes)
        
        if new_notes is not None: 
            data["tasks"][task_name]["notes"] = new_notes
            save_data(data)
            
            update_list()

def view_task_details():
    selected_task = task_listbox.get(tk.ACTIVE)
    if selected_task:
        task_name = selected_task.split(" - ")[0]
        if "(" in task_name:
            task_name = task_name.split(" (")[0]
        if "📝" in task_name:
            task_name = task_name.split(" 📝")[0]
            
        task_info = data["tasks"][task_name]
        
        details_window = tk.Toplevel(root)
        details_window.title(f"Details for '{task_name}'")
        details_window.geometry("400x300")
       
        tk.Label(details_window, text="Task:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Label(details_window, text=task_name).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        tk.Label(details_window, text="Recurring:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Label(details_window, text="Yes" if task_info["recurring"] else "No").grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        tk.Label(details_window, text="Times Completed:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Label(details_window, text=str(len(task_info["completions"]))).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        tk.Label(details_window, text="Notes:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.NW, padx=10, pady=5)
        
        notes_text = tk.Text(details_window, wrap=tk.WORD, width=30, height=8)
        notes_text.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        notes_text.insert(tk.END, task_info.get("notes", ""))
        notes_text.config(state=tk.DISABLED)  
      
        def edit_from_details():
            new_notes = simpledialog.askstring("Edit Notes", 
                                             f"Notes for '{task_name}':",
                                             initialvalue=task_info.get("notes", ""))
            if new_notes is not None:
                task_info["notes"] = new_notes
                notes_text.config(state=tk.NORMAL)
                notes_text.delete(1.0, tk.END)
                notes_text.insert(tk.END, new_notes)
                notes_text.config(state=tk.DISABLED)
                save_data(data)
                update_list()
        
        button_frame = tk.Frame(details_window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        edit_notes_btn = tk.Button(button_frame, text="Edit Notes", command=edit_from_details)
        edit_notes_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", command=details_window.destroy)
        close_btn.pack(side=tk.LEFT, padx=5)

def add_four_month_goal():
    goal = simpledialog.askstring("Add 4-Month Goal", "Enter goal description:")
    if goal and goal not in data["four_month_goals"]:
        target_date = simpledialog.askstring("Target Date", 
                                            "Enter target completion date (YYYY-MM-DD):",
                                            initialvalue=str(date.today() + timedelta(days=120)))
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
            data["four_month_goals"][goal] = {
                "target_date": target_date,
                "completed": False,
                "completion_date": None
            }
            update_four_month_goals_list()
            save_data(data)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

def edit_four_month_goal():
    selected_goal = four_month_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        new_goal = simpledialog.askstring("Edit Goal", "Edit goal description:", initialvalue=goal_name)
        
        if new_goal and new_goal != goal_name:
            if new_goal in data["four_month_goals"]:
                messagebox.showerror("Error", "This goal already exists.")
                return
                
            data["four_month_goals"][new_goal] = data["four_month_goals"][goal_name]
            del data["four_month_goals"][goal_name]
            
            target_date = simpledialog.askstring("Target Date", 
                                               "Enter target completion date (YYYY-MM-DD):",
                                               initialvalue=data["four_month_goals"][new_goal]["target_date"])
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
                data["four_month_goals"][new_goal]["target_date"] = target_date
                update_four_month_goals_list()
                save_data(data)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

def toggle_four_month_goal_completion():
    selected_goal = four_month_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        current_state = data["four_month_goals"][goal_name]["completed"]
        data["four_month_goals"][goal_name]["completed"] = not current_state
        
        if not current_state: 
            data["four_month_goals"][goal_name]["completion_date"] = str(date.today())
        else:  
            data["four_month_goals"][goal_name]["completion_date"] = None
            
        update_four_month_goals_list()
        save_data(data)

def delete_four_month_goal():
    selected_goal = four_month_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{goal_name}'?")
        if confirm:
            del data["four_month_goals"][goal_name]
            update_four_month_goals_list()
            save_data(data)

def update_four_month_goals_list():
    four_month_listbox.delete(0, tk.END)
    
    sorted_goals = sorted(
        data["four_month_goals"].items(),
        key=lambda x: (x[1]["completed"], x[1]["target_date"])
    )
    
    for goal, info in sorted_goals:
        status = "✓" if info["completed"] else "□"
        target_date = info["target_date"]
        
        if not info["completed"]:
            try:
                target = datetime.strptime(target_date, "%Y-%m-%d").date()
                today = date.today()
                days_remaining = (target - today).days
                if days_remaining < 0:
                    days_info = f"OVERDUE by {abs(days_remaining)} days"
                else:
                    days_info = f"{days_remaining} days remaining"
            except ValueError:
                days_info = "Invalid date"
        else:
            completion_date = info["completion_date"]
            days_info = f"Completed on {completion_date}"
            
        four_month_listbox.insert(tk.END, f"{goal} | {status} | {target_date} | {days_info}")

def add_five_year_goal():
    goal = simpledialog.askstring("Add 5-Year Goal", "Enter goal description:")
    if goal and goal not in data["five_year_goals"]:
        target_date = simpledialog.askstring("Target Date", 
                                           "Enter target completion date (YYYY-MM-DD):",
                                           initialvalue=str(date.today() + timedelta(days=365*5)))
        try:
            datetime.strptime(target_date, "%Y-%m-%d")
            data["five_year_goals"][goal] = {
                "target_date": target_date,
                "completed": False,
                "completion_date": None,
                "milestones": []
            }
            update_five_year_goals_list()
            save_data(data)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

def edit_five_year_goal():
    selected_goal = five_year_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        new_goal = simpledialog.askstring("Edit Goal", "Edit goal description:", initialvalue=goal_name)
        
        if new_goal and new_goal != goal_name:
            if new_goal in data["five_year_goals"]:
                messagebox.showerror("Error", "This goal already exists.")
                return
                
            data["five_year_goals"][new_goal] = data["five_year_goals"][goal_name]
            del data["five_year_goals"][goal_name]
         
            target_date = simpledialog.askstring("Target Date", 
                                               "Enter target completion date (YYYY-MM-DD):",
                                               initialvalue=data["five_year_goals"][new_goal]["target_date"])
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
                data["five_year_goals"][new_goal]["target_date"] = target_date
                update_five_year_goals_list()
                save_data(data)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

def toggle_five_year_goal_completion():
    selected_goal = five_year_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        current_state = data["five_year_goals"][goal_name]["completed"]
        data["five_year_goals"][goal_name]["completed"] = not current_state
        
        if not current_state:  
            data["five_year_goals"][goal_name]["completion_date"] = str(date.today())
        else: 
            data["five_year_goals"][goal_name]["completion_date"] = None
            
        update_five_year_goals_list()
        save_data(data)

def delete_five_year_goal():
    selected_goal = five_year_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{goal_name}'?")
        if confirm:
            del data["five_year_goals"][goal_name]
            update_five_year_goals_list()
            save_data(data)

def add_milestone():
    selected_goal = five_year_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        milestone = simpledialog.askstring("Add Milestone", "Enter milestone description:")
        if milestone:
            target_date = simpledialog.askstring("Milestone Target", 
                                               "Enter target date for milestone (YYYY-MM-DD):",
                                               initialvalue=str(date.today() + timedelta(days=90)))
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
                data["five_year_goals"][goal_name]["milestones"].append({
                    "description": milestone,
                    "target_date": target_date,
                    "completed": False,
                    "completion_date": None
                })
                save_data(data)
                messagebox.showinfo("Success", f"Milestone added to '{goal_name}'")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")

def view_milestones():
    selected_goal = five_year_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        milestones = data["five_year_goals"][goal_name]["milestones"]
        
        milestone_window = tk.Toplevel(root)
        milestone_window.title(f"Milestones for '{goal_name}'")
        milestone_window.geometry("600x400")

        columns = ("Description", "Target Date", "Status", "Completion Date")
        milestone_tree = ttk.Treeview(milestone_window, columns=columns, show="headings")

        for col in columns:
            milestone_tree.heading(col, text=col)
            milestone_tree.column(col, width=140)

        for milestone in milestones:
            status = "Completed" if milestone["completed"] else "In Progress"
            completion_date = milestone["completion_date"] if milestone["completed"] else "-"
            milestone_tree.insert("", tk.END, values=(
                milestone["description"],
                milestone["target_date"],
                status,
                completion_date
            ))
        
        milestone_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = tk.Frame(milestone_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        def toggle_milestone():
            selected = milestone_tree.focus()
            if selected:
                values = milestone_tree.item(selected, "values")
                milestone_description = values[0]

                for i, milestone in enumerate(milestones):
                    if milestone["description"] == milestone_description:
                        milestone["completed"] = not milestone["completed"]
                        if milestone["completed"]:
                            milestone["completion_date"] = str(date.today())
                        else:
                            milestone["completion_date"] = None

                        status = "Completed" if milestone["completed"] else "In Progress"
                        completion_date = milestone["completion_date"] if milestone["completed"] else "-"
                        milestone_tree.item(selected, values=(
                            milestone_description,
                            milestone["target_date"],
                            status,
                            completion_date
                        ))
                        
                        save_data(data)
                        break
        
        toggle_btn = tk.Button(button_frame, text="Toggle Completion", command=toggle_milestone)
        toggle_btn.pack(side=tk.LEFT, padx=5)

        def delete_milestone():
            selected = milestone_tree.focus()
            if selected:
                values = milestone_tree.item(selected, "values")
                milestone_description = values[0]
                
                confirm = messagebox.askyesno("Confirm Delete", 
                                             f"Are you sure you want to delete milestone '{milestone_description}'?")
                if confirm:
                    for i, milestone in enumerate(milestones):
                        if milestone["description"] == milestone_description:
                            del milestones[i]
                            milestone_tree.delete(selected)
                            save_data(data)
                            break
        
        delete_btn = tk.Button(button_frame, text="Delete Milestone", command=delete_milestone)
        delete_btn.pack(side=tk.LEFT, padx=5)
   
        close_btn = tk.Button(button_frame, text="Close", command=milestone_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

def update_five_year_goals_list():
    five_year_listbox.delete(0, tk.END)
    
    sorted_goals = sorted(
        data["five_year_goals"].items(),
        key=lambda x: (x[1]["completed"], x[1]["target_date"])
    )
    
    for goal, info in sorted_goals:
        status = "✓" if info["completed"] else "□"
        target_date = info["target_date"]
        milestone_count = len(info["milestones"])
        completed_milestones = sum(1 for m in info["milestones"] if m["completed"])

        if not info["completed"]:
            try:
                target = datetime.strptime(target_date, "%Y-%m-%d").date()
                today = date.today()
                days_remaining = (target - today).days
                if days_remaining < 0:
                    days_info = f"OVERDUE by {abs(days_remaining)} days"
                else:
                    days_info = f"{days_remaining} days remaining"
            except ValueError:
                days_info = "Invalid date"
        else:
            completion_date = info["completion_date"]
            days_info = f"Completed on {completion_date}"
        
        milestones_info = f"[{completed_milestones}/{milestone_count} milestones]" if milestone_count > 0 else ""
        five_year_listbox.insert(tk.END, f"{goal} | {status} | {target_date} | {days_info} {milestones_info}")

def add_lifetime_goal():
    goal = simpledialog.askstring("Add Lifetime Goal", "Enter goal description:")
    if goal and goal not in data["lifetime_goals"]:
        notes = simpledialog.askstring("Goal Notes", "Add notes for this goal (optional):", initialvalue="")
        
        data["lifetime_goals"][goal] = {
            "notes": notes if notes else "",
            "completed": False,
            "completion_date": None,
            "milestones": []
        }
        update_lifetime_goals_list()
        save_data(data)

def edit_lifetime_goal():
    selected_goal = lifetime_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        new_goal = simpledialog.askstring("Edit Goal", "Edit goal description:", initialvalue=goal_name)
        
        if new_goal and new_goal != goal_name:
            if new_goal in data["lifetime_goals"]:
                messagebox.showerror("Error", "This goal already exists.")
                return

            data["lifetime_goals"][new_goal] = data["lifetime_goals"][goal_name]
            del data["lifetime_goals"][goal_name]
            
            update_lifetime_goals_list()
            save_data(data)

def toggle_lifetime_goal_completion():
    selected_goal = lifetime_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        current_state = data["lifetime_goals"][goal_name]["completed"]
        data["lifetime_goals"][goal_name]["completed"] = not current_state
        
        if not current_state: 
            data["lifetime_goals"][goal_name]["completion_date"] = str(date.today())
        else: 
            data["lifetime_goals"][goal_name]["completion_date"] = None
            
        update_lifetime_goals_list()
        save_data(data)

def delete_lifetime_goal():
    selected_goal = lifetime_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{goal_name}'?")
        if confirm:
            del data["lifetime_goals"][goal_name]
            update_lifetime_goals_list()
            save_data(data)

def edit_lifetime_goal_notes():
    selected_goal = lifetime_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        current_notes = data["lifetime_goals"][goal_name]["notes"]

        notes_window = tk.Toplevel(root)
        notes_window.title(f"Notes for '{goal_name}'")
        notes_window.geometry("600x400")

        notes_frame = tk.Frame(notes_window)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(notes_frame, text="Goal Notes:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        notes_text = tk.Text(notes_frame, wrap=tk.WORD, width=70, height=18)
        notes_text.pack(fill=tk.BOTH, expand=True)
        notes_text.insert(tk.END, current_notes)

        scrollbar = tk.Scrollbar(notes_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        notes_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=notes_text.yview)

        button_frame = tk.Frame(notes_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_notes():
            new_notes = notes_text.get(1.0, tk.END).strip()
            data["lifetime_goals"][goal_name]["notes"] = new_notes
            save_data(data)
            update_lifetime_goals_list()
            notes_window.destroy()
            messagebox.showinfo("Success", "Notes saved successfully.")
        
        save_button = tk.Button(button_frame, text="Save Notes", command=save_notes)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=notes_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)

def view_lifetime_details():
    selected_goal = lifetime_listbox.get(tk.ACTIVE)
    if selected_goal:
        goal_name = selected_goal.split(" | ")[0]
        goal_info = data["lifetime_goals"][goal_name]

        details_window = tk.Toplevel(root)
        details_window.title(f"Details for '{goal_name}'")
        details_window.geometry("600x400")

        details_frame = tk.Frame(details_window)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(details_frame, text="Goal:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Label(details_frame, text=goal_name, font=("Arial", 12)).grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(details_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        status_text = "Completed" if goal_info["completed"] else "In Progress"
        tk.Label(details_frame, text=status_text, font=("Arial", 12)).grid(row=1, column=1, sticky=tk.W, pady=5)

        if goal_info["completed"]:
            tk.Label(details_frame, text="Completed on:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
            tk.Label(details_frame, text=goal_info["completion_date"], font=("Arial", 12)).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        tk.Label(details_frame, text="Notes:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.NW, pady=5)
        
        notes_text = tk.Text(details_frame, wrap=tk.WORD, width=50, height=10)
        notes_text.grid(row=3, column=1, sticky=tk.W, pady=5)
        notes_text.insert(tk.END, goal_info["notes"])
        notes_text.config(state=tk.DISABLED)  
        
        notes_scroll = tk.Scrollbar(details_frame, command=notes_text.yview)
        notes_scroll.grid(row=3, column=2, sticky=tk.NS)
        notes_text.config(yscrollcommand=notes_scroll.set)
        
        button_frame = tk.Frame(details_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        edit_notes_btn = tk.Button(button_frame, text="Edit Notes", 
                                  command=lambda: edit_lifetime_goal_notes_from_details(goal_name, notes_text, details_window))
        edit_notes_btn.pack(side=tk.LEFT, padx=5)
        
        toggle_btn = tk.Button(button_frame, text="Toggle Completion", 
                              command=lambda: toggle_lifetime_from_details(goal_name, details_window))
        toggle_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", command=details_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

def edit_lifetime_goal_notes_from_details(goal_name, notes_text_widget, parent_window):
    current_notes = data["lifetime_goals"][goal_name]["notes"]
    
    notes_window = tk.Toplevel(parent_window)
    notes_window.title(f"Edit Notes for '{goal_name}'")
    notes_window.geometry("600x400")
    
    edit_text = tk.Text(notes_window, wrap=tk.WORD, width=70, height=18)
    edit_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    edit_text.insert(tk.END, current_notes)
    
    button_frame = tk.Frame(notes_window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def save_notes():
        new_notes = edit_text.get(1.0, tk.END).strip()
        data["lifetime_goals"][goal_name]["notes"] = new_notes
        save_data(data)
        
        notes_text_widget.config(state=tk.NORMAL)
        notes_text_widget.delete(1.0, tk.END)
        notes_text_widget.insert(tk.END, new_notes)
        notes_text_widget.config(state=tk.DISABLED)
        
        update_lifetime_goals_list()
        notes_window.destroy()
    
    save_button = tk.Button(button_frame, text="Save Notes", command=save_notes)
    save_button.pack(side=tk.LEFT, padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=notes_window.destroy)
    cancel_button.pack(side=tk.RIGHT, padx=5)

def toggle_lifetime_from_details(goal_name, window):
    current_state = data["lifetime_goals"][goal_name]["completed"]
    data["lifetime_goals"][goal_name]["completed"] = not current_state
    
    if not current_state:  
        data["lifetime_goals"][goal_name]["completion_date"] = str(date.today())
    else:  
        data["lifetime_goals"][goal_name]["completion_date"] = None
    
    update_lifetime_goals_list()
    save_data(data)

    window.destroy()
    view_lifetime_details()

def update_lifetime_goals_list():
    lifetime_listbox.delete(0, tk.END)

    sorted_goals = sorted(
        data["lifetime_goals"].items(),
        key=lambda x: x[1]["completed"]
    )
    
    for goal, info in sorted_goals:
        status = "✓" if info["completed"] else "□"
        notes_indicator = "📝" if info["notes"] else ""
        
        if info["completed"]:
            completion_info = f"Completed on {info['completion_date']}"
        else:
            completion_info = "In progress"
            
        lifetime_listbox.insert(tk.END, f"{goal} | {status} | {completion_info} {notes_indicator}")

def exit_app():
    save_data(data)
    root.destroy()

data = load_data()

root = tk.Tk()
root.title("Complete Goal Tracker")
root.geometry("800x600")

tab_control = ttk.Notebook(root)

todo_tab = ttk.Frame(tab_control)
four_month_tab = ttk.Frame(tab_control)
five_year_tab = ttk.Frame(tab_control)
lifetime_tab = ttk.Frame(tab_control)

tab_control.add(todo_tab, text='Daily Tasks')
tab_control.add(four_month_tab, text='4-Month Goals')
tab_control.add(five_year_tab, text='5-Year Goals')
tab_control.add(lifetime_tab, text='Lifetime Goals') 

tab_control.pack(expand=1, fill='both')

task_listbox = tk.Listbox(todo_tab, width=50, height=15, font=("Arial", 10))
task_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
update_list()

button_frame = tk.Frame(todo_tab)
button_frame.pack(padx=10, pady=5, fill=tk.X)

add_button = tk.Button(button_frame, text="Add Task", command=add_task)
add_button.pack(side=tk.LEFT, padx=5)

done_button = tk.Button(button_frame, text="Mark Completed", command=mark_completed)
done_button.pack(side=tk.LEFT, padx=5)

view_details_button = tk.Button(button_frame, text="View Details", command=view_task_details)
view_details_button.pack(side=tk.LEFT, padx=5)

edit_notes_button = tk.Button(button_frame, text="Edit Notes", command=edit_notes)
edit_notes_button.pack(side=tk.LEFT, padx=5)

edit_button = tk.Button(button_frame, text="Edit Task", command=edit_task)
edit_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(button_frame, text="Delete Task", command=delete_task)
delete_button.pack(side=tk.LEFT, padx=5)

toggle_button = tk.Button(button_frame, text="Toggle Recurring", command=toggle_recurring)
toggle_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=exit_app)
exit_button.pack(side=tk.RIGHT, padx=5)

four_month_listbox = tk.Listbox(four_month_tab, width=80, height=15, font=("Arial", 10))
four_month_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

four_month_button_frame = tk.Frame(four_month_tab)
four_month_button_frame.pack(padx=10, pady=5, fill=tk.X)

add_four_month_button = tk.Button(four_month_button_frame, text="Add Goal", command=add_four_month_goal)
add_four_month_button.pack(side=tk.LEFT, padx=5)

edit_four_month_button = tk.Button(four_month_button_frame, text="Edit Goal", command=edit_four_month_goal)
edit_four_month_button.pack(side=tk.LEFT, padx=5)

toggle_four_month_button = tk.Button(four_month_button_frame, text="Toggle Completion", 
                                    command=toggle_four_month_goal_completion)
toggle_four_month_button.pack(side=tk.LEFT, padx=5)

delete_four_month_button = tk.Button(four_month_button_frame, text="Delete Goal", command=delete_four_month_goal)
delete_four_month_button.pack(side=tk.LEFT, padx=5)

five_year_listbox = tk.Listbox(five_year_tab, width=80, height=15, font=("Arial", 10))
five_year_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

five_year_button_frame = tk.Frame(five_year_tab)
five_year_button_frame.pack(padx=10, pady=5, fill=tk.X)

add_five_year_button = tk.Button(five_year_button_frame, text="Add Goal", command=add_five_year_goal)
add_five_year_button.pack(side=tk.LEFT, padx=5)

edit_five_year_button = tk.Button(five_year_button_frame, text="Edit Goal", command=edit_five_year_goal)
edit_five_year_button.pack(side=tk.LEFT, padx=5)

toggle_five_year_button = tk.Button(five_year_button_frame, text="Toggle Completion", 
                                   command=toggle_five_year_goal_completion)
toggle_five_year_button.pack(side=tk.LEFT, padx=5)

add_milestone_button = tk.Button(five_year_button_frame, text="Add Milestone", command=add_milestone)
add_milestone_button.pack(side=tk.LEFT, padx=5)

view_milestones_button = tk.Button(five_year_button_frame, text="View Milestones", command=view_milestones)
view_milestones_button.pack(side=tk.LEFT, padx=5)

delete_five_year_button = tk.Button(five_year_button_frame, text="Delete Goal", command=delete_five_year_goal)
delete_five_year_button.pack(side=tk.LEFT, padx=5)

lifetime_listbox = tk.Listbox(lifetime_tab, width=80, height=15, font=("Arial", 10))
lifetime_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

lifetime_button_frame = tk.Frame(lifetime_tab)
lifetime_button_frame.pack(padx=10, pady=5, fill=tk.X)

add_lifetime_button = tk.Button(lifetime_button_frame, text="Add Goal", command=add_lifetime_goal)
add_lifetime_button.pack(side=tk.LEFT, padx=5)

edit_lifetime_button = tk.Button(lifetime_button_frame, text="Edit Goal", command=edit_lifetime_goal)
edit_lifetime_button.pack(side=tk.LEFT, padx=5)

view_details_button = tk.Button(lifetime_button_frame, text="View Details", command=view_lifetime_details)
view_details_button.pack(side=tk.LEFT, padx=5)

edit_notes_button = tk.Button(lifetime_button_frame, text="Edit Notes", command=edit_lifetime_goal_notes)
edit_notes_button.pack(side=tk.LEFT, padx=5)

toggle_lifetime_button = tk.Button(lifetime_button_frame, text="Toggle Completion", 
                               command=toggle_lifetime_goal_completion)
toggle_lifetime_button.pack(side=tk.LEFT, padx=5)

delete_lifetime_button = tk.Button(lifetime_button_frame, text="Delete Goal", command=delete_lifetime_goal)
delete_lifetime_button.pack(side=tk.LEFT, padx=5)

if "four_month_goals" not in data:
    data["four_month_goals"] = {}
if "five_year_goals" not in data:
    data["five_year_goals"] = {}
if "lifetime_goals" not in data:
    data["lifetime_goals"] = {}
    
update_four_month_goals_list()
update_five_year_goals_list()
update_lifetime_goals_list()

root.mainloop()