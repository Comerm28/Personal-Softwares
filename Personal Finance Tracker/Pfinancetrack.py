import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os
from datetime import datetime

# Constants
DATA_FILE = "Personal Finance Tracker/finance_data.json"
DEFAULT_CURRENCY = "$"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Data file is corrupted. Starting with empty data.")
    
    # Default data structure
    return {
        "accounts": {},
        "transactions": [],
        "settings": {
            "currency": DEFAULT_CURRENCY
        }
    }

def save_data(data):
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_account():
    account_name = simpledialog.askstring("Add Account", "Enter account name:")
    if account_name and account_name not in data["accounts"]:
        initial_balance = simpledialog.askfloat("Initial Balance", 
                                              f"Enter initial balance for {account_name}:", 
                                              initialvalue=0.00)
        if initial_balance is not None:  # User didn't cancel
            data["accounts"][account_name] = float(initial_balance)
            update_accounts_list()
            save_data(data)
            update_summary()
    elif account_name in data["accounts"]:
        messagebox.showerror("Error", f"Account '{account_name}' already exists.")

def delete_account():
    selected_account = accounts_listbox.get(tk.ACTIVE)
    if selected_account:
        account_name = selected_account.split(":")[0].strip()
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete '{account_name}' account?")
        if confirm:
            del data["accounts"][account_name]
            update_accounts_list()
            save_data(data)
            update_summary()
            messagebox.showinfo("Success", f"Account '{account_name}' deleted.")

def update_balance():
    selected_account = accounts_listbox.get(tk.ACTIVE)
    if selected_account:
        account_name = selected_account.split(":")[0].strip()
        current_balance = data["accounts"][account_name]
        
        new_balance = simpledialog.askfloat("Update Balance", 
                                          f"Enter new balance for {account_name}:", 
                                          initialvalue=current_balance)
        
        if new_balance is not None:  # User didn't cancel
            # Record transaction for the change
            change_amount = new_balance - current_balance
            
            # Update the account balance
            data["accounts"][account_name] = float(new_balance)
            
            # Add transaction record
            data["transactions"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "account": account_name,
                "amount": change_amount,
                "type": "deposit" if change_amount > 0 else "withdrawal",
                "description": f"Manual balance update"
            })
            
            update_accounts_list()
            update_transaction_history()
            save_data(data)
            update_summary()

def update_accounts_list():
    accounts_listbox.delete(0, tk.END)
    currency = data["settings"]["currency"]
    
    for account, balance in data["accounts"].items():
        accounts_listbox.insert(tk.END, f"{account}: {currency}{balance:.2f}")

def update_transaction_history():
    # Clear the transaction treeview
    for item in transaction_tree.get_children():
        transaction_tree.delete(item)
    
    # Sort transactions by date (most recent first)
    sorted_transactions = sorted(
        data["transactions"], 
        key=lambda x: x["date"], 
        reverse=True
    )
    
    # Show only the most recent 100 transactions
    for transaction in sorted_transactions[:100]:
        amount = transaction["amount"]
        amount_str = f"{data['settings']['currency']}{abs(amount):.2f}"
        
        # Color code: green for deposits, red for withdrawals
        tag = "deposit" if amount > 0 else "withdrawal"
        
        transaction_tree.insert("", tk.END, values=(
            transaction["date"],
            transaction["account"],
            amount_str,
            transaction["type"],
            transaction["description"]
        ), tags=(tag,))
    
    # Configure tag colors
    transaction_tree.tag_configure("deposit", foreground="green")
    transaction_tree.tag_configure("withdrawal", foreground="red")

def update_summary():
    total_balance = sum(data["accounts"].values())
    currency = data["settings"]["currency"]
    
    # Update summary labels
    total_label.config(text=f"Total Balance: {currency}{total_balance:.2f}")
    
    # Count accounts
    account_count = len(data["accounts"])
    account_label.config(text=f"Number of Accounts: {account_count}")
    
    # Update networth history if needed
    # (This could be expanded to track net worth over time)

def exit_app():
    save_data(data)
    root.destroy()

# Load data
data = load_data()

# Create the main window
root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("800x600")

# Create tab control
tab_control = ttk.Notebook(root)

# Create tabs
accounts_tab = ttk.Frame(tab_control)
summary_tab = ttk.Frame(tab_control)

tab_control.add(accounts_tab, text='Accounts')
tab_control.add(summary_tab, text='Summary')

tab_control.pack(expand=1, fill='both')

# Accounts Tab
accounts_frame = ttk.LabelFrame(accounts_tab, text="Your Accounts")
accounts_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

accounts_listbox = tk.Listbox(accounts_frame, width=50, height=10, font=("Arial", 10))
accounts_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Account buttons
button_frame = ttk.Frame(accounts_frame)
button_frame.pack(padx=10, pady=5, fill=tk.X)

add_button = ttk.Button(button_frame, text="Add Account", command=add_account)
add_button.pack(side=tk.LEFT, padx=5)

update_button = ttk.Button(button_frame, text="Update Balance", command=update_balance)
update_button.pack(side=tk.LEFT, padx=5)

delete_button = ttk.Button(button_frame, text="Delete Account", command=delete_account)
delete_button.pack(side=tk.LEFT, padx=5)

exit_button = ttk.Button(button_frame, text="Exit", command=exit_app)
exit_button.pack(side=tk.RIGHT, padx=5)

# Summary Tab
summary_frame = ttk.LabelFrame(summary_tab, text="Financial Summary")
summary_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Summary information
total_label = ttk.Label(summary_frame, text="Total Balance: $0.00", font=("Arial", 14, "bold"))
total_label.pack(pady=10)

account_label = ttk.Label(summary_frame, text="Number of Accounts: 0", font=("Arial", 12))
account_label.pack(pady=5)

# Transaction history
transactions_frame = ttk.LabelFrame(summary_tab, text="Recent Transactions")
transactions_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a treeview for transactions
columns = ("Date", "Account", "Amount", "Type", "Description")
transaction_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings", height=10)

# Define column headings and widths
transaction_tree.heading("Date", text="Date")
transaction_tree.heading("Account", text="Account")
transaction_tree.heading("Amount", text="Amount")
transaction_tree.heading("Type", text="Type")
transaction_tree.heading("Description", text="Description")

transaction_tree.column("Date", width=140)
transaction_tree.column("Account", width=100)
transaction_tree.column("Amount", width=80)
transaction_tree.column("Type", width=80)
transaction_tree.column("Description", width=200)

transaction_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Initialize the UI
update_accounts_list()
update_transaction_history()
update_summary()

# Start the app
root.mainloop()