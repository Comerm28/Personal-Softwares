import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quarterly Budget Tracker")
        self.root.geometry("900x700")
        
        # Colors - Matching your Journal App style
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#5c6bc0"
        self.highlight_color = "#7986cb"
        self.income_color = "#66bb6a"
        self.expense_color = "#ef5350"
        
        self.root.configure(bg=self.bg_color)
        self.setup_styles()
        
        self.data = self.load_data()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_fg, font=("Arial", 10))
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#444444", foreground="#ffffff", padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)])
        
        # Treeview (Table) Styling
        style.configure("Treeview", background=self.text_bg, foreground=self.text_fg, fieldbackground=self.text_bg, rowheight=25)
        style.map("Treeview", background=[('selected', self.highlight_color)])
        style.configure("Treeview.Heading", background="#444444", foreground="white", relief="flat")

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.root)
        self.summary_tab = ttk.Frame(self.tabs)
        self.entry_tab = ttk.Frame(self.tabs)
        
        self.tabs.add(self.summary_tab, text="Dashboard")
        self.tabs.add(self.entry_tab, text="Add Transaction")
        self.tabs.pack(expand=1, fill='both')

        self.setup_summary_tab()
        self.setup_entry_tab()

    def setup_summary_tab(self):
        # Header / Quarter Selector
        top_frame = tk.Frame(self.summary_tab, bg=self.bg_color, pady=20)
        top_frame.pack(fill='x')
        
        tk.Label(top_frame, text="Quarterly Overview", font=("Arial", 18, "bold"), 
                 bg=self.bg_color, fg=self.text_fg).pack(side=tk.LEFT, padx=20)
        
        self.q_var = tk.StringVar(value=self.get_current_quarter())
        q_selector = ttk.Combobox(top_frame, textvariable=self.q_var, values=["Q1", "Q2", "Q3", "Q4"], width=5)
        q_selector.pack(side=tk.RIGHT, padx=20)
        q_selector.bind("<<ComboboxSelected>>", lambda e: self.refresh_dashboard())

        # Stats Cards
        self.stats_frame = tk.Frame(self.summary_tab, bg=self.bg_color)
        self.stats_frame.pack(fill='x', padx=20)
        
        self.income_label = self.create_stat_card(self.stats_frame, "Total Income", "0.00", self.income_color, 0)
        self.expense_label = self.create_stat_card(self.stats_frame, "Total Expenses", "0.00", self.expense_color, 1)
        self.balance_label = self.create_stat_card(self.stats_frame, "Remaining", "0.00", self.accent_color, 2)

        # Transaction Table
        self.tree = ttk.Treeview(self.summary_tab, columns=("Date", "Category", "Amount", "Type"), show='headings')
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Type", text="Type")
        self.tree.pack(expand=1, fill='both', padx=20, pady=20)
        
        self.refresh_dashboard()

    def create_stat_card(self, parent, label, value, color, col):
        f = tk.Frame(parent, bg=self.text_bg, highlightbackground=color, highlightthickness=2, padx=20, pady=15)
        f.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        
        tk.Label(f, text=label, bg=self.text_bg, fg="#aaaaaa", font=("Arial", 10)).pack()
        v_lbl = tk.Label(f, text=f"${value}", bg=self.text_bg, fg=color, font=("Arial", 16, "bold"))
        v_lbl.pack()
        return v_lbl

    def setup_entry_tab(self):
        container = tk.Frame(self.entry_tab, bg=self.bg_color)
        container.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        labels = ["Date (YYYY-MM-DD):", "Category:", "Amount:", "Type:"]
        self.inputs = {}

        for i, text in enumerate(labels):
            tk.Label(container, text=text, pady=10).grid(row=i, column=0, sticky="e")
            
        self.date_ent = tk.Entry(container, bg=self.text_bg, fg="white", insertbackground="white", borderwidth=0)
        self.date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_ent.grid(row=0, column=1, padx=10, pady=10)
        
        self.cat_ent = tk.Entry(container, bg=self.text_bg, fg="white", insertbackground="white", borderwidth=0)
        self.cat_ent.grid(row=1, column=1, padx=10, pady=10)
        
        self.amt_ent = tk.Entry(container, bg=self.text_bg, fg="white", insertbackground="white", borderwidth=0)
        self.amt_ent.grid(row=2, column=1, padx=10, pady=10)
        
        self.type_var = tk.StringVar(value="Expense")
        type_dropdown = ttk.Combobox(container, textvariable=self.type_var, values=["Income", "Expense"])
        type_dropdown.grid(row=3, column=1, padx=10, pady=10)
        
        btn = tk.Button(container, text="Add Transaction", command=self.add_transaction,
                       bg=self.accent_color, fg="white", relief=tk.FLAT, padx=20, pady=10)
        btn.grid(row=4, column=0, columnspan=2, pady=30)

    def get_current_quarter(self):
        month = datetime.now().month
        return f"Q{(month-1)//3 + 1}"

    def add_transaction(self):
        try:
            date_str = self.date_ent.get()
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            quarter = f"Q{(date_obj.month-1)//3 + 1}"
            
            entry = {
                "date": date_str,
                "category": self.cat_ent.get(),
                "amount": float(self.amt_ent.get()),
                "type": self.type_var.get(),
                "quarter": quarter
            }
            
            self.data.append(entry)
            self.save_data()
            
            # Reset form
            self.cat_ent.delete(0, tk.END)
            self.amt_ent.delete(0, tk.END)
            messagebox.showinfo("Success", "Transaction recorded!")
            self.refresh_dashboard()
            self.tabs.select(0)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount and date (YYYY-MM-DD)")

    def refresh_dashboard(self):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        selected_q = self.q_var.get()
        income = 0
        expenses = 0
        
        for item in self.data:
            if item['quarter'] == selected_q:
                self.tree.insert("", tk.END, values=(item['date'], item['category'], f"${item['amount']:.2f}", item['type']))
                if item['type'] == "Income":
                    income += item['amount']
                else:
                    expenses += item['amount']
        
        self.income_label.config(text=f"${income:.2f}")
        self.expense_label.config(text=f"${expenses:.2f}")
        self.balance_label.config(text=f"${(income - expenses):.2f}")

    def load_data(self):
        try:
            with open('budget/budget_data.json', 'r') as f:
                return json.load(f)
        except:
            return []

    def save_data(self):
        with open('budget/budget_data.json', 'w') as f:
            json.dump(self.data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()