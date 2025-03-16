import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from datetime import datetime

class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Journal App")
        
        self.entries = self.load_entries()
        
        self.create_widgets()
        
    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.entry_tab = ttk.Frame(self.tab_control)
        self.view_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.entry_tab, text='New Entry')
        self.tab_control.add(self.view_tab, text='Past Journals')
        
        self.tab_control.pack(expand=1, fill='both')
        
        # Entry Tab
        self.entry_text = tk.Text(self.entry_tab, wrap='word', height=15)
        self.entry_text.pack(padx=10, pady=10)
        
        self.save_button = tk.Button(self.entry_tab, text="Save Entry", command=self.save_entry)
        self.save_button.pack(pady=10)
        
        # View Tab
        self.journal_list = tk.Listbox(self.view_tab)
        self.journal_list.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.load_journal_list()
        
    def save_entry(self):
        entry_content = self.entry_text.get("1.0", tk.END).strip()
        if entry_content:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.entries.append({"date": entry_date, "content": entry_content})
            self.save_entries()
            self.entry_text.delete("1.0", tk.END)
            self.load_journal_list()
            messagebox.showinfo("Success", "Journal entry saved!")
        else:
            messagebox.showwarning("Warning", "Entry cannot be empty!")
    
    def load_entries(self):
        try:
            with open('journal_entries.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    def save_entries(self):
        with open('journal_entries.json', 'w') as file:
            json.dump(self.entries, file, indent=4)
    
    def load_journal_list(self):
        self.journal_list.delete(0, tk.END)
        for entry in self.entries:
            self.journal_list.insert(tk.END, f"{entry['date']}: {entry['content'][:30]}...")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()