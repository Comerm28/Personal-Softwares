import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import json
import os
from PIL import Image, ImageTk

# Attempt to register HEIC support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False

SLOTS_PER_POUCH = 36
COLS = 9
ROWS = 4
SLOT_SIZE = 64 # pixels

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_data.json")
EXTERNAL_PATH = "D:/inventory"

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Tracker")
        self.root.geometry("1000x600+50+50")
        self.root.configure(bg="#2c2c2c") # Darker, more polished background
        
        self.data = self.load_data()
        self.current_pouch = None
        self.image_cache = {}
        
        # Styles
        self.setup_styles()
        self.setup_ui()
        
        if self.data:
            self.current_pouch = list(self.data.keys())[0]
            self.refresh_pouch_list()
            self.pouch_listbox.selection_set(0)
            self.load_pouch(self.current_pouch)
        else:
            self.add_pouch("General")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#2c2c2c")
        style.configure("Pouch.TFrame", background="#3c3c3c", relief="flat")
        style.configure("TLabel", background="#2c2c2c", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#2c2c2c")
        style.configure("TButton", font=("Segoe UI", 10))
        
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Migrate old data format and ensure 'pouch' attribute
                    for pouch_name, items in data.items():
                        for i in range(len(items)):
                            item = items[i]
                            if isinstance(item, str):
                                data[pouch_name][i] = {"name": item, "count": 1, "image": None, "pouch": pouch_name}
                            elif item and "pouch" not in item:
                                item["pouch"] = pouch_name
                    return data
            except Exception:
                pass
        return {}

    def save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def setup_ui(self):
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left side for pouches (Polished Menu)
        self.left_frame = tk.Frame(self.main_container, width=250, bg="#333333", bd=0)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)
        
        tk.Label(self.left_frame, text="INVENTORY", bg="#333333", fg="#00d2ff", font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        self.pouch_listbox = tk.Listbox(
            self.left_frame, 
            font=("Segoe UI", 11), 
            bg="#333333", 
            fg="#eeeeee", 
            borderwidth=0, 
            highlightthickness=0,
            selectbackground="#00d2ff",
            selectforeground="#000000",
            activestyle='none'
        )
        self.pouch_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.pouch_listbox.bind('<<ListboxSelect>>', self.on_pouch_select)
        
        btn_container = tk.Frame(self.left_frame, bg="#333333")
        btn_container.pack(fill=tk.X, padx=20, pady=20)
        
        self.btn_add_pouch = tk.Button(
            btn_container, text="+ New Pouch", font=("Segoe UI", 10, "bold"),
            bg="#444444", fg="white", relief="flat", bd=0, pady=8,
            activebackground="#555555", activeforeground="white",
            command=self.prompt_add_pouch
        )
        self.btn_add_pouch.pack(fill=tk.X, pady=5)
        
        self.btn_del_pouch = tk.Button(
            btn_container, text="- Delete Pouch", font=("Segoe UI", 10),
            bg="#444444", fg="#ff6b6b", relief="flat", bd=0, pady=5,
            activebackground="#555555", activeforeground="#ff6b6b",
            command=self.delete_current_pouch
        )
        self.btn_del_pouch.pack(fill=tk.X, pady=5)

        # Right side for slots
        self.right_frame = tk.Frame(self.main_container, bg="#2c2c2c")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.pouch_title = tk.Label(self.right_frame, text="Select a Pouch", font=("Segoe UI", 24, "bold"), bg="#2c2c2c", fg="white")
        self.pouch_title.pack(pady=(30, 10))
        
        # Minecraft-style container
        self.slots_outer = tk.Frame(self.right_frame, bg="#1e1e1e", bd=2, relief="flat")
        self.slots_outer.pack(pady=20, padx=20)
        
        self.slots_frame = tk.Frame(self.slots_outer, bg="#8b8b8b", bd=4, relief="sunken")
        self.slots_frame.pack()
        
        self.slot_widgets = []
        for r in range(ROWS):
            for c in range(COLS):
                idx = r * COLS + c
                # A slot is a canvas to allow overlaying images and text
                canvas = tk.Canvas(
                    self.slots_frame, width=SLOT_SIZE, height=SLOT_SIZE,
                    bg="#c6c6c6", highlightthickness=0, relief="raised", bd=3
                )
                canvas.grid(row=r, column=c, padx=2, pady=2)
                canvas.bind("<Button-1>", lambda e, i=idx: self.on_slot_click(i))
                self.slot_widgets.append(canvas)

    def refresh_pouch_list(self):
        self.pouch_listbox.delete(0, tk.END)
        for p in self.data.keys():
            self.pouch_listbox.insert(tk.END, p)

    def prompt_add_pouch(self):
        name = simpledialog.askstring("Add Pouch", "Enter new pouch name:", parent=self.root)
        if name:
            name = name.strip()
            if name in self.data:
                messagebox.showerror("Error", "Pouch already exists!", parent=self.root)
            elif name:
                self.add_pouch(name)

    def add_pouch(self, name):
        self.data[name] = [None] * SLOTS_PER_POUCH
        self.save_data()
        self.refresh_pouch_list()
        
        idx = list(self.data.keys()).index(name)
        self.pouch_listbox.selection_clear(0, tk.END)
        self.pouch_listbox.selection_set(idx)
        self.load_pouch(name)

    def delete_current_pouch(self):
        if not self.current_pouch:
            return
        if messagebox.askyesno("Confirm", f"Delete pouch '{self.current_pouch}' and all its items?", parent=self.root):
            del self.data[self.current_pouch]
            self.save_data()
            self.refresh_pouch_list()
            if self.data:
                first_pouch = list(self.data.keys())[0]
                self.pouch_listbox.selection_set(0)
                self.load_pouch(first_pouch)
            else:
                self.current_pouch = None
                self.pouch_title.config(text="Select a Pouch")
                self.clear_slots()

    def on_pouch_select(self, event):
        selection = self.pouch_listbox.curselection()
        if selection:
            idx = selection[0]
            pouch_name = self.pouch_listbox.get(idx)
            self.load_pouch(pouch_name)

    def get_image(self, img_path):
        if not img_path: return None
        
        full_path = os.path.join(EXTERNAL_PATH, img_path)
        if full_path in self.image_cache:
            return self.image_cache[full_path]
        
        if not os.path.exists(full_path):
            return None
            
        try:
            img = Image.open(full_path)
            # Resize and crop to fill slot while keeping aspect ratio
            w, h = img.size
            aspect = w / h
            if aspect > 1: # Wide
                new_w = int(SLOT_SIZE * aspect)
                img = img.resize((new_w, SLOT_SIZE), Image.Resampling.LANCZOS)
                left = (new_w - SLOT_SIZE) / 2
                img = img.crop((left, 0, left + SLOT_SIZE, SLOT_SIZE))
            else: # Tall
                new_h = int(SLOT_SIZE / aspect)
                img = img.resize((SLOT_SIZE, new_h), Image.Resampling.LANCZOS)
                top = (new_h - SLOT_SIZE) / 2
                img = img.crop((0, top, SLOT_SIZE, top + SLOT_SIZE))
            
            photo = ImageTk.PhotoImage(img)
            self.image_cache[full_path] = photo
            return photo
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            return None

    def load_pouch(self, name):
        self.current_pouch = name
        self.pouch_title.config(text=name.upper())
        items = self.data.get(name, [None] * SLOTS_PER_POUCH)
        for i, canvas in enumerate(self.slot_widgets):
            canvas.delete("all")
            if i < len(items):
                item = items[i]
                if item:
                    # Draw Image
                    photo = self.get_image(item.get("image"))
                    if photo:
                        canvas.create_image(SLOT_SIZE//2, SLOT_SIZE//2, image=photo)
                    else:
                        # Fallback to text if no image
                        name_text = item["name"]
                        display_text = name_text if len(name_text) <= 8 else name_text[:6] + ".."
                        canvas.create_text(SLOT_SIZE//2, SLOT_SIZE//2, text=display_text, fill="black", font=("Arial", 8, "bold"), width=SLOT_SIZE-4)
                    
                    # Draw Count (bottom right)
                    count = item.get("count", 1)
                    if count > 1:
                        # Minecraft style count shadow
                        canvas.create_text(SLOT_SIZE-4, SLOT_SIZE-4, text=str(count), fill="#3f3f3f", font=("Arial", 12, "bold"), anchor="se")
                        canvas.create_text(SLOT_SIZE-6, SLOT_SIZE-6, text=str(count), fill="white", font=("Arial", 12, "bold"), anchor="se")
                    
                    canvas.config(bg="#a0c0e0", relief="raised")
                else:
                    canvas.config(bg="#c6c6c6", relief="raised")
            else:
                canvas.config(bg="#8b8b8b", relief="flat")

    def clear_slots(self):
        for canvas in self.slot_widgets:
            canvas.delete("all")
            canvas.config(bg="#8b8b8b", relief="flat")

    def on_slot_click(self, index):
        if not self.current_pouch:
            return
        
        current_item = self.data[self.current_pouch][index]
        pouch_list = list(self.data.keys())
        dialog = EditItemDialog(self.root, current_item, pouch_list, self.current_pouch)
        self.root.wait_window(dialog)
        
        if dialog.result == 'clear':
            self.data[self.current_pouch][index] = None
            self.save_data()
            self.load_pouch(self.current_pouch)
        elif dialog.result == 'save' and dialog.item_data:
            new_pouch = dialog.item_data.get("pouch")
            
            # Check if moving to a different pouch
            if new_pouch and new_pouch != self.current_pouch:
                target_items = self.data[new_pouch]
                try:
                    empty_idx = target_items.index(None)
                    self.data[new_pouch][empty_idx] = dialog.item_data
                    self.data[self.current_pouch][index] = None
                    messagebox.showinfo("Success", f"Moved to {new_pouch}")
                except ValueError:
                    messagebox.showerror("Error", f"Pouch '{new_pouch}' is full!")
                    return 
            else:
                self.data[self.current_pouch][index] = dialog.item_data
                
            self.save_data()
            self.load_pouch(self.current_pouch)

class EditItemDialog(tk.Toplevel):
    def __init__(self, parent, item_data, pouch_list, current_pouch):
        super().__init__(parent)
        self.title("Item Details")
        self.geometry("400x520+50+50")
        self.configure(bg="#2c2c2c")
        self.result = None
        self.item_data = item_data or {"name": "", "count": 1, "image": None, "pouch": current_pouch}
        if "pouch" not in self.item_data:
            self.item_data["pouch"] = current_pouch
        
        # UI Elements
        tk.Label(self, text="Item Name:", bg="#2c2c2c", fg="white").pack(pady=(20, 0))
        self.ent_name = tk.Entry(self, font=("Segoe UI", 12))
        self.ent_name.insert(0, self.item_data["name"])
        self.ent_name.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(self, text="Pouch:", bg="#2c2c2c", fg="white").pack(pady=(10, 0))
        self.cb_pouch = ttk.Combobox(self, values=pouch_list, state="readonly", font=("Segoe UI", 11))
        self.cb_pouch.set(self.item_data["pouch"])
        self.cb_pouch.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(self, text="Count:", bg="#2c2c2c", fg="white").pack(pady=(10, 0))
        self.ent_count = tk.Entry(self, font=("Segoe UI", 12))
        self.ent_count.insert(0, str(self.item_data["count"]))
        self.ent_count.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(self, text="Image Path (relative to D:/inventory):", bg="#2c2c2c", fg="white").pack(pady=(10, 0))
        self.img_frame = tk.Frame(self, bg="#2c2c2c")
        self.img_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.ent_image = tk.Entry(self.img_frame, font=("Segoe UI", 10))
        self.ent_image.insert(0, self.item_data["image"] or "")
        self.ent_image.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(self.img_frame, text="Browse", command=self.browse_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Preview
        self.preview_label = tk.Label(self, text="No Preview", bg="#3c3c3c", width=20, height=8)
        self.preview_label.pack(pady=20)
        self.update_preview()
        
        btn_frame = tk.Frame(self, bg="#2c2c2c")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Save", width=10, bg="#00d2ff", fg="black", font=("Segoe UI", 10, "bold"), command=self.save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Remove", width=10, bg="#ff6b6b", fg="white", command=self.clear_slot).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", width=10, command=self.destroy).pack(side=tk.LEFT, padx=10)
        
        self.transient(parent)
        self.grab_set()

    def browse_image(self):
        initial_dir = EXTERNAL_PATH if os.path.exists(EXTERNAL_PATH) else "/"
        file_types = [("Images", "*.jpg *.jpeg *.png *.heic *.HEIC")]
        filename = filedialog.askopenfilename(initialdir=initial_dir, title="Select Item Image", filetypes=file_types)
        
        if filename:
            if filename.lower().startswith(EXTERNAL_PATH.lower()):
                rel_path = os.path.relpath(filename, EXTERNAL_PATH)
                self.ent_image.delete(0, tk.END)
                self.ent_image.insert(0, rel_path)
                self.update_preview()
            else:
                messagebox.showwarning("Warning", f"Please select an image from {EXTERNAL_PATH}")

    def update_preview(self):
        img_path = self.ent_image.get()
        if not img_path: return
        
        full_path = os.path.join(EXTERNAL_PATH, img_path)
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                img.thumbnail((150, 150))
                self.photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.photo, text="")
            except Exception:
                self.preview_label.config(text="Error loading image", image="")
        else:
            self.preview_label.config(text="Image not found", image="")

    def save(self):
        try:
            count = int(self.ent_count.get())
        except ValueError:
            count = 1
            
        self.item_data = {
            "name": self.ent_name.get().strip(),
            "count": count,
            "image": self.ent_image.get().strip() or None,
            "pouch": self.cb_pouch.get()
        }
        if not self.item_data["name"]:
            messagebox.showerror("Error", "Name is required")
            return
            
        self.result = 'save'
        self.destroy()

    def clear_slot(self):
        self.result = 'clear'
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    app = InventoryApp(root)
    root.mainloop()
