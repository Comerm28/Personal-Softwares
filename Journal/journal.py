import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from datetime import datetime

class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Journal App")
        self.root.geometry("800x600")  # Set a default size
        
        # Dark mode colors
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#5c6bc0"  # A nice purple-blue color
        self.highlight_color = "#7986cb"
        
        # Apply theme to root window
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use('default')  # Start with default theme as base
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", 
                            background="#444444", 
                            foreground="#ffffff",
                            padding=[10, 2],
                            font=("Arial", 10))

        # Override the tab colors more explicitly
        self.style.map("TNotebook.Tab", 
                      background=[("selected", self.accent_color), ("!selected", "#444444")],
                      foreground=[("selected", "#ffffff"), ("!selected", "#ffffff")])
        
        self.entries = self.load_entries()
        
        self.create_widgets()
        
    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.entry_tab = ttk.Frame(self.tab_control)
        self.view_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.entry_tab, text='New Entry')
        self.tab_control.add(self.view_tab, text='Past Journals')
        
        self.tab_control.pack(expand=1, fill='both')
        
        # Configure the entry tab to expand properly
        self.entry_tab.columnconfigure(0, weight=1)
        self.entry_tab.rowconfigure(0, weight=1)
        
        # Entry Tab with expandable text area
        self.entry_text = tk.Text(self.entry_tab, wrap='word', bg=self.text_bg, fg=self.text_fg, 
                                insertbackground=self.text_fg, font=("Arial", 11))
        self.entry_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to entry text
        entry_scrollbar = tk.Scrollbar(self.entry_tab, command=self.entry_text.yview)
        entry_scrollbar.grid(row=0, column=1, sticky="ns")
        self.entry_text['yscrollcommand'] = entry_scrollbar.set
        
        # Button frame in entry tab
        entry_button_frame = tk.Frame(self.entry_tab, bg=self.bg_color)
        entry_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.save_button = tk.Button(entry_button_frame, text="Save Entry", command=self.save_entry,
                                   bg=self.accent_color, fg="white", activebackground=self.highlight_color,
                                   activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                   padx=10, pady=5)
        self.save_button.pack()
        
        # Configure the view tab to expand properly
        self.view_tab.columnconfigure(0, weight=1)
        self.view_tab.rowconfigure(0, weight=1)
        
        # View Tab with expandable list
        self.journal_list = tk.Listbox(self.view_tab, font=("Arial", 10), bg=self.text_bg, fg=self.text_fg,
                                    selectbackground=self.accent_color, selectforeground="white")
        self.journal_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Add scrollbar to journal list
        list_scrollbar = tk.Scrollbar(self.view_tab, command=self.journal_list.yview)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.journal_list['yscrollcommand'] = list_scrollbar.set
        
        # Button frame in view tab
        view_button_frame = tk.Frame(self.view_tab, bg=self.bg_color)
        view_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        button_style = {"bg": self.accent_color, "fg": "white", "activebackground": self.highlight_color,
                       "activeforeground": "white", "font": ("Arial", 10), "relief": tk.FLAT,
                       "padx": 10, "pady": 5}
        
        self.open_button = tk.Button(view_button_frame, text="Open Entry", command=self.open_entry, **button_style)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(view_button_frame, text="Delete Entry", command=self.delete_entry, **button_style)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.load_journal_list()
        
    def save_entry(self):
        entry_content = self.entry_text.get("1.0", tk.END).strip()
        if entry_content:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Calculate and store word count at save time
            word_count = len(entry_content.split())
            self.entries.append({
                "date": entry_date,
                "content": entry_content,
                "word_count": word_count  # Cache the word count
            })
            self.save_entries()
            self.entry_text.delete("1.0", tk.END)
            self.load_journal_list()
            messagebox.showinfo("Success", "Journal entry saved!")
        else:
            messagebox.showwarning("Warning", "Entry cannot be empty!")
    
    def load_entries(self):
        try:
            with open('Journal/journal_entries.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
    
    def save_entries(self):
        with open('Journal/journal_entries.json', 'w') as file:
            json.dump(self.entries, file, indent=4)
    
    def load_journal_list(self):
        self.journal_list.delete(0, tk.END)
        
        # Sort entries by date, most recent first
        sorted_entries = sorted(self.entries, key=lambda x: x['date'], reverse=True)
        
        for entry in sorted_entries:
            # Use the cached word count if available, otherwise calculate it
            if "word_count" not in entry:
                # For backwards compatibility with older entries
                entry["word_count"] = len(entry["content"].split())
            
            # Display date with word count
            self.journal_list.insert(tk.END, f"{entry['date']} | {entry['word_count']} words")
    
    def open_entry(self):
        selected_index = self.journal_list.curselection()
        if selected_index:
            # Get the corresponding entry from the sorted list
            sorted_entries = sorted(self.entries, key=lambda x: x['date'], reverse=True)
            entry = sorted_entries[selected_index[0]]
            self.show_entry_window(entry)
        else:
            messagebox.showwarning("Warning", "No entry selected!")
    
    def show_entry_window(self, entry):
        entry_window = tk.Toplevel(self.root)
        entry_window.title(f"Journal Entry - {entry['date']}")
        entry_window.geometry("800x600")  # Set a default size
        entry_window.configure(bg=self.bg_color)
        
        # Make the window resizable
        entry_window.columnconfigure(0, weight=1)
        entry_window.rowconfigure(0, weight=1)
        
        # Content frame
        content_frame = tk.Frame(entry_window, bg=self.bg_color)
        content_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Date label
        date_label = tk.Label(content_frame, text=entry['date'], font=("Arial", 12, "bold"),
                             bg=self.bg_color, fg=self.text_fg)
        date_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Text frame with scrollbar
        text_frame = tk.Frame(content_frame, bg=self.bg_color)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        entry_text = tk.Text(text_frame, wrap='word', font=("Arial", 11),
                           padx=10, pady=10, bg=self.text_bg, fg=self.text_fg, relief=tk.FLAT)
        entry_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(text_frame, command=entry_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        entry_text.config(yscrollcommand=scrollbar.set)
        
        entry_text.insert(tk.END, entry['content'])
        entry_text.config(state=tk.DISABLED)
        
        # Button frame
        button_frame = tk.Frame(entry_window, bg=self.bg_color)
        button_frame.grid(row=1, column=0, pady=10)
        
        close_button = tk.Button(button_frame, text="Close", command=entry_window.destroy,
                               width=10, font=("Arial", 10), bg=self.accent_color, fg="white",
                               activebackground=self.highlight_color, activeforeground="white",
                               relief=tk.FLAT, padx=10, pady=5)
        close_button.pack()
        
    def delete_entry(self):
        selected_index = self.journal_list.curselection()
        if selected_index:
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
            if confirm:
                # Get the corresponding entry from the sorted list
                sorted_entries = sorted(self.entries, key=lambda x: x['date'], reverse=True)
                entry_to_delete = sorted_entries[selected_index[0]]
                
                # Find and remove this entry from the main list
                for i, entry in enumerate(self.entries):
                    if entry['date'] == entry_to_delete['date']:
                        del self.entries[i]
                        break
                
                self.save_entries()
                self.load_journal_list()
                messagebox.showinfo("Success", "Journal entry deleted!")
        else:
            messagebox.showwarning("Warning", "No entry selected!")

if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()