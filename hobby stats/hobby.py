import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class HobbyProgressApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hobby Progress & Hours Tracker")
        self.root.geometry("900x600")
        
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#4caf50" 
        self.highlight_color = "#81c784"
        
        self.data_path = os.path.join("hobby stats", "progress_data.json")
        self.hobbies = self.load_data()
        self.create_widgets()

    def create_widgets(self):
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(header, text="My Hobby Progress", font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.text_fg).pack(side=tk.LEFT)

        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="+ Add Hobby", command=self.open_edit_window, bg=self.accent_color, fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Progress", command=self.open_edit_selected, bg="#666666", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)

        body = tk.Frame(self.root, bg=self.bg_color)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(body, bg=self.text_bg, fg=self.text_fg, selectbackground=self.accent_color, font=("Arial", 11), borderwidth=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._update_preview())

        self.preview_text = tk.Text(body, width=40, bg=self.text_bg, fg=self.text_fg, state=tk.DISABLED, font=("Arial", 10), padx=10, pady=10)
        self.preview_text.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.refresh_listbox()

    def load_data(self):
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, "r") as f: return json.load(f)
        except: pass
        return []

    def save_data(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f: json.dump(self.hobbies, f, indent=4)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for h in self.hobbies:
            self.listbox.insert(tk.END, f" {h['level']}% | {h['name']} ({h['hours']} hrs)")

    def open_edit_selected(self):
        sel = self.listbox.curselection()
        if sel: self.open_edit_window(self.hobbies[sel[0]])

    def open_edit_window(self, hobby=None):
        is_edit = hobby is not None
        w = tk.Toplevel(self.root)
        w.title("Update Progress")
        w.geometry("400x500")
        w.configure(bg=self.bg_color)

        tk.Label(w, text="Hobby Name:", bg=self.bg_color, fg=self.text_fg).pack(pady=(15, 0))
        name_ent = tk.Entry(w, bg=self.text_bg, fg=self.text_fg, insertbackground="white")
        name_ent.pack(fill=tk.X, padx=30, pady=5)
        if is_edit: name_ent.insert(0, hobby['name'])

        tk.Label(w, text="Total Hours Invested:", bg=self.bg_color, fg=self.text_fg).pack(pady=(10, 0))
        hours_ent = tk.Spinbox(w, from_=0, to=99999, bg=self.text_bg, fg=self.text_fg)
        hours_ent.pack(pady=5)
        if is_edit: 
            hours_ent.delete(0, tk.END)
            hours_ent.insert(0, hobby['hours'])

        tk.Label(w, text="Skill Proficiency (0-100%):", bg=self.bg_color, fg=self.text_fg).pack(pady=(10, 0))
        level_scale = tk.Scale(w, from_=0, to=100, orient=tk.HORIZONTAL, bg=self.bg_color, fg=self.text_fg, highlightthickness=0)
        level_scale.pack(fill=tk.X, padx=30)
        if is_edit: level_scale.set(hobby['level'])

        tk.Label(w, text="Milestones / Creations:", bg=self.bg_color, fg=self.text_fg).pack(pady=(10, 0))
        notes_txt = tk.Text(w, height=8, bg=self.text_bg, fg=self.text_fg)
        notes_txt.pack(fill=tk.BOTH, padx=30, pady=5)
        if is_edit: notes_txt.insert(tk.END, hobby['notes'])

        def save():
            data = {
                "id": hobby['id'] if is_edit else str(datetime.now().timestamp()),
                "name": name_ent.get(),
                "hours": hours_ent.get(),
                "level": level_scale.get(),
                "notes": notes_txt.get(1.0, tk.END).strip()
            }
            if is_edit:
                idx = next(i for i, h in enumerate(self.hobbies) if h['id'] == hobby['id'])
                self.hobbies[idx] = data
            else:
                self.hobbies.append(data)
            self.save_data()
            self.refresh_listbox()
            w.destroy()

        tk.Button(w, text="Save Progress", command=save, bg=self.accent_color, fg="white", relief=tk.FLAT).pack(pady=20)

    def _update_preview(self):
        sel = self.listbox.curselection()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        if sel:
            h = self.hobbies[sel[0]]
            preview = f"ACTIVITY: {h['name']}\n"
            preview += f"TIME SPENT: {h['hours']} Hours\n"
            preview += f"MASTERY: {h['level']}%\n"
            preview += "-"*30 + "\n"
            preview += f"MILESTONES & CREATIONS:\n\n{h['notes']}"
            self.preview_text.insert(tk.END, preview)
        self.preview_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = HobbyProgressApp(root)
    root.mainloop()