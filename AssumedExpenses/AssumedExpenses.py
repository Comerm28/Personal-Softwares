# ...existing code...
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class AssumedExpensesApp:
    FREQUENCIES = ["Weekly", "Monthly", "Yearly", "Once"]
    PURCHASES_PER_YEAR = {"Weekly": 52, "Monthly": 12, "Yearly": 1, "Once": 0}  # Once handled separately

    def __init__(self, root):
        self.root = root
        self.root.title("Assumed Expenses")
        self.root.geometry("800x600")

        # styling (dark theme similar to provided file)
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#d35400"
        self.highlight_color = "#e67e22"

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

        self.expenses = self.load_expenses()
        self.create_widgets()
        self.load_expense_list()
        self.update_total()

    def create_widgets(self):
        # Top: years to calculate
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top_frame, text="Calculate for (years):", bg=self.bg_color, fg=self.text_fg,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        self.years_var = tk.IntVar(value=1)
        self.years_spin = tk.Spinbox(top_frame, from_=1, to=100, textvariable=self.years_var,
                                     width=5, bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                     relief=tk.FLAT, font=("Arial", 10), command=self.on_years_changed)
        self.years_spin.pack(side=tk.LEFT, padx=(8, 0))

        # Main Notebook: Add / View
        self.tab_control = ttk.Notebook(self.root)
        self.add_tab = ttk.Frame(self.tab_control)
        self.view_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.add_tab, text="New Expense")
        self.tab_control.add(self.view_tab, text="My Expenses")
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=(5,10))

        # New Expense Tab
        name_frame = tk.Frame(self.add_tab, bg=self.bg_color)
        name_frame.pack(fill="x", pady=(10,5))
        tk.Label(name_frame, text="Item Name:", bg=self.bg_color, fg=self.text_fg).pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                   relief=tk.FLAT, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=8, fill="x", expand=True)

        cost_frame = tk.Frame(self.add_tab, bg=self.bg_color)
        cost_frame.pack(fill="x", pady=5)
        tk.Label(cost_frame, text="Cost (per purchase):", bg=self.bg_color, fg=self.text_fg).pack(side=tk.LEFT)
        self.cost_entry = tk.Entry(cost_frame, bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                   relief=tk.FLAT, width=15)
        self.cost_entry.pack(side=tk.LEFT, padx=8)

        freq_frame = tk.Frame(self.add_tab, bg=self.bg_color)
        freq_frame.pack(fill="x", pady=5)
        tk.Label(freq_frame, text="Frequency:", bg=self.bg_color, fg=self.text_fg).pack(side=tk.LEFT)
        self.freq_combo = ttk.Combobox(freq_frame, values=self.FREQUENCIES, state="readonly", width=12)
        self.freq_combo.current(1)  # default Monthly
        self.freq_combo.pack(side=tk.LEFT, padx=8)

        btn_frame = tk.Frame(self.add_tab, bg=self.bg_color)
        btn_frame.pack(pady=12)
        save_btn = tk.Button(btn_frame, text="Save Expense", command=self.save_expense,
                             bg=self.accent_color, fg="white", activebackground=self.highlight_color,
                             activeforeground="white", font=("Arial", 10), relief=tk.FLAT, padx=10, pady=5)
        save_btn.pack(side=tk.LEFT, padx=5)
        clear_btn = tk.Button(btn_frame, text="Clear", command=self.clear_form,
                              bg="#777777", fg="white", activebackground="#999999",
                              activeforeground="white", font=("Arial", 10), relief=tk.FLAT, padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # View Tab: list and actions
        self.view_tab.columnconfigure(0, weight=1)
        self.view_tab.rowconfigure(0, weight=1)
        self.expense_list = tk.Listbox(self.view_tab, font=("Arial", 10), bg=self.text_bg, fg=self.text_fg,
                                       selectbackground=self.accent_color, selectforeground="white")
        self.expense_list.grid(row=0, column=0, sticky="nsew", padx=(10,0), pady=10)
        list_scroll = tk.Scrollbar(self.view_tab, command=self.expense_list.yview)
        list_scroll.grid(row=0, column=1, sticky="ns", pady=10)
        self.expense_list['yscrollcommand'] = list_scroll.set

        action_frame = tk.Frame(self.view_tab, bg=self.bg_color)
        action_frame.grid(row=1, column=0, columnspan=2, pady=(0,10))
        btn_style = {"bg": self.accent_color, "fg": "white", "activebackground": self.highlight_color,
                     "activeforeground": "white", "font": ("Arial", 10), "relief": tk.FLAT, "padx": 10, "pady": 5}
        view_btn = tk.Button(action_frame, text="View", command=self.view_expense, **btn_style)
        view_btn.pack(side=tk.LEFT, padx=5)
        edit_btn = tk.Button(action_frame, text="Edit", command=self.edit_expense, **btn_style)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = tk.Button(action_frame, text="Delete", command=self.delete_expense, **btn_style)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Bottom: total
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=10, pady=(0,10))
        tk.Label(bottom_frame, text="Total over selected years:", bg=self.bg_color, fg=self.text_fg,
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.total_var = tk.StringVar(value="$0.00")
        tk.Label(bottom_frame, textvariable=self.total_var, bg=self.bg_color, fg=self.accent_color,
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)

    def on_years_changed(self):
        try:
            years = int(self.years_var.get())
            if years < 1:
                self.years_var.set(1)
        except Exception:
            self.years_var.set(1)
        self.update_total()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.freq_combo.current(1)
        if hasattr(self, 'editing_index'):
            delattr(self, 'editing_index')

    def save_expense(self):
        name = self.name_entry.get().strip()
        cost_text = self.cost_entry.get().strip()
        freq = self.freq_combo.get()

        if not name:
            messagebox.showwarning("Warning", "Item name cannot be empty!")
            return
        try:
            cost = float(cost_text)
            if cost < 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Warning", "Cost must be a non-negative number!")
            return

        expense_obj = {"name": name, "cost": cost, "frequency": freq}

        if hasattr(self, 'editing_index'):
            self.expenses[self.editing_index] = expense_obj
            delattr(self, 'editing_index')
        else:
            self.expenses.append(expense_obj)

        self.save_expenses()
        self.clear_form()
        self.load_expense_list()
        self.update_total()
        messagebox.showinfo("Success", f"Expense '{name}' saved.")

    def load_expenses(self):
        try:
            folder = "AssumedExpenses"
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = os.path.join(folder, "expenses.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {e}")
            return []

    def save_expenses(self):
        try:
            folder = "AssumedExpenses"
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = os.path.join(folder, "expenses.json")
            with open(path, "w") as f:
                json.dump(self.expenses, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expenses: {e}")

    def load_expense_list(self):
        self.expense_list.delete(0, tk.END)
        for e in sorted(self.expenses, key=lambda x: x["name"]):
            display = f"{e['name']} | ${e['cost']:.2f} | {e['frequency']}"
            self.expense_list.insert(tk.END, display)

    def find_expense_by_name(self, name):
        for i, e in enumerate(self.expenses):
            if e["name"] == name:
                return i, e
        return None, None

    def view_expense(self):
        sel = self.expense_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No expense selected!")
            return
        display = self.expense_list.get(sel[0])
        name = display.split(" | ")[0]
        _, e = self.find_expense_by_name(name)
        if not e:
            messagebox.showerror("Error", "Expense not found.")
            return

        w = tk.Toplevel(self.root)
        w.title(f"Expense: {e['name']}")
        w.geometry("400x220")
        w.configure(bg=self.bg_color)
        tk.Label(w, text=e['name'], font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.text_fg).pack(anchor="w", padx=15, pady=(15,0))
        tk.Label(w, text=f"Cost per purchase: ${e['cost']:.2f}", bg=self.bg_color, fg=self.text_fg, font=("Arial", 11)).pack(anchor="w", padx=15, pady=6)
        tk.Label(w, text=f"Frequency: {e['frequency']}", bg=self.bg_color, fg=self.text_fg, font=("Arial", 11)).pack(anchor="w", padx=15)
        # show computed over selected years
        years = max(1, int(self.years_var.get()))
        purchases = self._purchases_for_frequency(e['frequency'], years)
        total_cost = purchases * e['cost']
        tk.Label(w, text=f"Purchases over {years} year(s): {purchases}", bg=self.bg_color, fg=self.text_fg, font=("Arial", 11)).pack(anchor="w", padx=15, pady=(10,0))
        tk.Label(w, text=f"Total for this item: ${total_cost:.2f}", bg=self.bg_color, fg=self.accent_color, font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(6,10))
        tk.Button(w, text="Close", command=w.destroy, bg=self.accent_color, fg="white", relief=tk.FLAT, padx=10, pady=5).pack(pady=(0,15))

    def edit_expense(self):
        sel = self.expense_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No expense selected!")
            return
        display = self.expense_list.get(sel[0])
        name = display.split(" | ")[0]
        idx, e = self.find_expense_by_name(name)
        if e is None:
            messagebox.showerror("Error", "Expense not found.")
            return
        # switch to Add tab and populate
        self.tab_control.select(0)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, e["name"])
        self.cost_entry.delete(0, tk.END)
        self.cost_entry.insert(0, f"{e['cost']:.2f}")
        try:
            self.freq_combo.current(self.FREQUENCIES.index(e["frequency"]))
        except ValueError:
            self.freq_combo.current(1)
        self.editing_index = idx

    def delete_expense(self):
        sel = self.expense_list.curselection()
        if not sel:
            messagebox.showwarning("Warning", "No expense selected!")
            return
        display = self.expense_list.get(sel[0])
        name = display.split(" | ")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{name}'?")
        if not confirm:
            return
        idx, _ = self.find_expense_by_name(name)
        if idx is not None:
            del self.expenses[idx]
            self.save_expenses()
            self.load_expense_list()
            self.update_total()
            messagebox.showinfo("Success", f"'{name}' deleted.")

    def _purchases_for_frequency(self, frequency, years):
        if frequency == "Once":
            return 1 if years >= 1 else 0
        per_year = self.PURCHASES_PER_YEAR.get(frequency, 0)
        return per_year * years

    def update_total(self):
        years = max(1, int(self.years_var.get()))
        total = 0.0
        for e in self.expenses:
            purchases = self._purchases_for_frequency(e["frequency"], years)
            total += purchases * float(e["cost"])
        self.total_var.set(f"${total:,.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssumedExpensesApp(root)
    root.mainloop()