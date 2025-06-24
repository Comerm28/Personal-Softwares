import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import json
import os

class CookingApp:
    def __init__(self, root):
        # Initialize the Cooking app with dark mode and UI setup
        self.root = root
        self.root.title("Recipe Collection")
        self.root.geometry("800x600")
        
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
        
        self.recipes = self.load_recipes()
        self.create_widgets()
        
    def create_widgets(self):
        # Create the UI widgets for the Cooking app
        self.tab_control = ttk.Notebook(self.root)
        
        self.new_recipe_tab = ttk.Frame(self.tab_control)
        self.view_recipes_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.new_recipe_tab, text='New Recipe')
        self.tab_control.add(self.view_recipes_tab, text='My Recipes')
        
        self.tab_control.pack(expand=1, fill='both')
        
        self.new_recipe_tab.columnconfigure(0, weight=1)
        self.new_recipe_tab.rowconfigure(2, weight=1)
        
        name_frame = tk.Frame(self.new_recipe_tab, bg=self.bg_color)
        name_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        
        tk.Label(name_frame, text="Recipe Name:", bg=self.bg_color, fg=self.text_fg, 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0,5))
        
        self.recipe_name_entry = tk.Entry(name_frame, bg=self.text_bg, fg=self.text_fg, 
                                        insertbackground=self.text_fg, font=("Arial", 10),
                                        relief=tk.FLAT, width=40)
        self.recipe_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ingredients_frame = tk.Frame(self.new_recipe_tab, bg=self.bg_color)
        ingredients_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        tk.Label(ingredients_frame, text="Ingredients:", bg=self.bg_color, fg=self.text_fg, 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0,5))
        
        self.ingredients_text = tk.Text(ingredients_frame, height=5, bg=self.text_bg, fg=self.text_fg, 
                                      insertbackground=self.text_fg, font=("Arial", 10),
                                      relief=tk.FLAT, wrap="word")
        self.ingredients_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ingredients_scrollbar = tk.Scrollbar(ingredients_frame, command=self.ingredients_text.yview)
        ingredients_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.ingredients_text['yscrollcommand'] = ingredients_scrollbar.set
        
        tk.Label(self.new_recipe_tab, text="Instructions:", bg=self.bg_color, fg=self.text_fg, 
                font=("Arial", 10, "bold")).grid(row=2, column=0, padx=10, pady=(5,0), sticky="nw")
        
        instructions_frame = tk.Frame(self.new_recipe_tab, bg=self.bg_color)
        instructions_frame.grid(row=3, column=0, padx=10, pady=(0,10), sticky="nsew")
        instructions_frame.columnconfigure(0, weight=1)
        instructions_frame.rowconfigure(0, weight=1)
        
        self.instructions_text = tk.Text(instructions_frame, wrap='word', bg=self.text_bg, fg=self.text_fg, 
                                      insertbackground=self.text_fg, font=("Arial", 11))
        self.instructions_text.grid(row=0, column=0, sticky="nsew")
        
        instructions_scrollbar = tk.Scrollbar(instructions_frame, command=self.instructions_text.yview)
        instructions_scrollbar.grid(row=0, column=1, sticky="ns")
        self.instructions_text['yscrollcommand'] = instructions_scrollbar.set
        
        button_frame = tk.Frame(self.new_recipe_tab, bg=self.bg_color)
        button_frame.grid(row=4, column=0, pady=10)
        
        self.save_button = tk.Button(button_frame, text="Save Recipe", command=self.save_recipe,
                                   bg=self.accent_color, fg="white", activebackground=self.highlight_color,
                                   activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                   padx=10, pady=5)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(button_frame, text="Clear Form", command=self.clear_form,
                                    bg="#777777", fg="white", activebackground="#999999",
                                    activeforeground="white", font=("Arial", 10), relief=tk.FLAT,
                                    padx=10, pady=5)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.view_recipes_tab.columnconfigure(0, weight=1)
        self.view_recipes_tab.rowconfigure(0, weight=1)
        
        self.recipe_list = tk.Listbox(self.view_recipes_tab, font=("Arial", 10), bg=self.text_bg, fg=self.text_fg,
                                   selectbackground=self.accent_color, selectforeground="white")
        self.recipe_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        list_scrollbar = tk.Scrollbar(self.view_recipes_tab, command=self.recipe_list.yview)
        list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.recipe_list['yscrollcommand'] = list_scrollbar.set
        
        view_button_frame = tk.Frame(self.view_recipes_tab, bg=self.bg_color)
        view_button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        button_style = {"bg": self.accent_color, "fg": "white", "activebackground": self.highlight_color,
                       "activeforeground": "white", "font": ("Arial", 10), "relief": tk.FLAT,
                       "padx": 10, "pady": 5}
        
        self.view_button = tk.Button(view_button_frame, text="View Recipe", command=self.view_recipe, **button_style)
        self.view_button.pack(side=tk.LEFT, padx=5)
        
        self.ingredients_button = tk.Button(view_button_frame, text="Just Ingredients", 
                                         command=self.view_ingredients, **button_style)
        self.ingredients_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_button = tk.Button(view_button_frame, text="Edit Recipe", command=self.edit_recipe, **button_style)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(view_button_frame, text="Delete Recipe", command=self.delete_recipe, **button_style)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.load_recipe_list()
        
    def save_recipe(self):
        # Save a new recipe or update an existing one
        recipe_name = self.recipe_name_entry.get().strip()
        ingredients = self.ingredients_text.get("1.0", tk.END).strip()
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        
        if not recipe_name:
            messagebox.showwarning("Warning", "Recipe name cannot be empty!")
            return
            
        if not ingredients:
            messagebox.showwarning("Warning", "Ingredients cannot be empty!")
            return
            
        if not instructions:
            messagebox.showwarning("Warning", "Instructions cannot be empty!")
            return
        
        editing = False
        for i, recipe in enumerate(self.recipes):
            if recipe["name"] == self.editing_recipe_name if hasattr(self, 'editing_recipe_name') else None:
                self.recipes[i] = {
                    "name": recipe_name,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "ingredient_count": len(ingredients.split('\n'))
                }
                editing = True
                if hasattr(self, 'editing_recipe_name'):
                    delattr(self, 'editing_recipe_name')
                break
        
        if not editing:
            self.recipes.append({
                "name": recipe_name,
                "ingredients": ingredients,
                "instructions": instructions,
                "ingredient_count": len(ingredients.split('\n'))
            })
        
        self.save_recipes()
        self.clear_form()
        self.load_recipe_list()
        messagebox.showinfo("Success", f"Recipe '{recipe_name}' saved!")
        
    def clear_form(self):
        # Clear the recipe entry form
        self.recipe_name_entry.delete(0, tk.END)
        self.ingredients_text.delete("1.0", tk.END)
        self.instructions_text.delete("1.0", tk.END)
        if hasattr(self, 'editing_recipe_name'):
            delattr(self, 'editing_recipe_name')
        
    def load_recipes(self):
        # Load recipes from the JSON file
        try:
            if not os.path.exists("Cooking"):
                os.makedirs("Cooking")
                
            if os.path.exists("Cooking/recipes.json"):
                with open("Cooking/recipes.json", "r") as file:
                    return json.load(file)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recipes: {str(e)}")
            return []
    
    def save_recipes(self):
        # Save recipes to the JSON file
        try:
            if not os.path.exists("Cooking"):
                os.makedirs("Cooking")
                
            with open("Cooking/recipes.json", "w") as file:
                json.dump(self.recipes, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recipes: {str(e)}")
    
    def load_recipe_list(self):
        # Load the recipe list into the UI
        self.recipe_list.delete(0, tk.END)
        sorted_recipes = sorted(self.recipes, key=lambda x: x["name"])
        for recipe in sorted_recipes:
            ingredient_count = recipe.get("ingredient_count", len(recipe["ingredients"].split('\n')))
            self.recipe_list.insert(tk.END, f"{recipe['name']} | {ingredient_count} ingredients")
    
    def view_recipe(self):
        # View the full recipe details
        selected_index = self.recipe_list.curselection()
        if selected_index:
            recipe_name = self.recipe_list.get(selected_index[0]).split(" | ")[0]
            recipe = self.find_recipe_by_name(recipe_name)
            if recipe:
                self.show_recipe_window(recipe)
        else:
            messagebox.showwarning("Warning", "No recipe selected!")
    
    def view_ingredients(self):
        # View only the ingredients of a recipe
        selected_index = self.recipe_list.curselection()
        if selected_index:
            recipe_name = self.recipe_list.get(selected_index[0]).split(" | ")[0]
            recipe = self.find_recipe_by_name(recipe_name)
            if recipe:
                self.show_ingredients_window(recipe)
        else:
            messagebox.showwarning("Warning", "No recipe selected!")
    
    def edit_recipe(self):
        # Edit an existing recipe
        selected_index = self.recipe_list.curselection()
        if selected_index:
            recipe_name = self.recipe_list.get(selected_index[0]).split(" | ")[0]
            recipe = self.find_recipe_by_name(recipe_name)
            if recipe:
                self.tab_control.select(0)
                self.recipe_name_entry.delete(0, tk.END)
                self.recipe_name_entry.insert(0, recipe["name"])
                self.ingredients_text.delete("1.0", tk.END)
                self.ingredients_text.insert("1.0", recipe["ingredients"])
                self.instructions_text.delete("1.0", tk.END)
                self.instructions_text.insert("1.0", recipe["instructions"])
                self.editing_recipe_name = recipe["name"]
        else:
            messagebox.showwarning("Warning", "No recipe selected!")
    
    def delete_recipe(self):
        # Delete a recipe from the collection
        selected_index = self.recipe_list.curselection()
        if selected_index:
            recipe_name = self.recipe_list.get(selected_index[0]).split(" | ")[0]
            confirm = messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete the recipe '{recipe_name}'?")
            if confirm:
                for i, recipe in enumerate(self.recipes):
                    if recipe["name"] == recipe_name:
                        del self.recipes[i]
                        break
                self.save_recipes()
                self.load_recipe_list()
                messagebox.showinfo("Success", f"Recipe '{recipe_name}' deleted!")
        else:
            messagebox.showwarning("Warning", "No recipe selected!")
    
    def find_recipe_by_name(self, name):
        # Find a recipe by its name
        for recipe in self.recipes:
            if recipe["name"] == name:
                return recipe
        return None
    
    def show_recipe_window(self, recipe):
        # Show the full recipe details in a new window
        recipe_window = tk.Toplevel(self.root)
        recipe_window.title(f"Recipe: {recipe['name']}")
        recipe_window.geometry("800x600")
        recipe_window.configure(bg=self.bg_color)
        
        recipe_window.columnconfigure(0, weight=1)
        recipe_window.rowconfigure(1, weight=1)
        
        header_frame = tk.Frame(recipe_window, bg=self.bg_color)
        header_frame.grid(row=0, column=0, padx=15, pady=(15,5), sticky="ew")
        
        recipe_name_label = tk.Label(header_frame, text=recipe['name'], font=("Arial", 16, "bold"),
                                   bg=self.bg_color, fg=self.text_fg)
        recipe_name_label.pack(anchor="w")
        
        content_frame = tk.Frame(recipe_window, bg=self.bg_color)
        content_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        tk.Label(content_frame, text="Ingredients:", font=("Arial", 12, "bold"),
               bg=self.bg_color, fg=self.text_fg).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        ingredients_frame = tk.Frame(content_frame, bg=self.bg_color)
        ingredients_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.rowconfigure(0, weight=1)
        
        ingredients_text = tk.Text(ingredients_frame, wrap='word', height=8, font=("Arial", 10),
                                 bg=self.text_bg, fg=self.text_fg, relief=tk.FLAT)
        ingredients_text.grid(row=0, column=0, sticky="nsew")
        
        ingredients_scrollbar = tk.Scrollbar(ingredients_frame, command=ingredients_text.yview)
        ingredients_scrollbar.grid(row=0, column=1, sticky="ns")
        ingredients_text.config(yscrollcommand=ingredients_scrollbar.set)
        
        ingredients_text.insert(tk.END, recipe['ingredients'])
        ingredients_text.config(state=tk.DISABLED)
        
        tk.Label(content_frame, text="Instructions:", font=("Arial", 12, "bold"),
               bg=self.bg_color, fg=self.text_fg).grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        instructions_frame = tk.Frame(content_frame, bg=self.bg_color)
        instructions_frame.grid(row=3, column=0, sticky="nsew")
        instructions_frame.columnconfigure(0, weight=1)
        instructions_frame.rowconfigure(0, weight=1)
        
        instructions_text = tk.Text(instructions_frame, wrap='word', font=("Arial", 10),
                                  bg=self.text_bg, fg=self.text_fg, relief=tk.FLAT)
        instructions_text.grid(row=0, column=0, sticky="nsew")
        
        instructions_scrollbar = tk.Scrollbar(instructions_frame, command=instructions_text.yview)
        instructions_scrollbar.grid(row=0, column=1, sticky="ns")
        instructions_text.config(yscrollcommand=instructions_scrollbar.set)
        
        instructions_text.insert(tk.END, recipe['instructions'])
        instructions_text.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(recipe_window, bg=self.bg_color)
        button_frame.grid(row=2, column=0, pady=10)
        
        close_button = tk.Button(button_frame, text="Close", command=recipe_window.destroy,
                               width=10, font=("Arial", 10), bg=self.accent_color, fg="white",
                               activebackground=self.highlight_color, activeforeground="white",
                               relief=tk.FLAT, padx=10, pady=5)
        close_button.pack()
    
    def show_ingredients_window(self, recipe):
        # Show only the ingredients of a recipe in a new window
        ingredients_window = tk.Toplevel(self.root)
        ingredients_window.title(f"Ingredients for: {recipe['name']}")
        ingredients_window.geometry("500x400")
        ingredients_window.configure(bg=self.bg_color)
        
        ingredients_window.columnconfigure(0, weight=1)
        ingredients_window.rowconfigure(1, weight=1)
        
        header_frame = tk.Frame(ingredients_window, bg=self.bg_color)
        header_frame.grid(row=0, column=0, padx=15, pady=(15,5), sticky="ew")
        
        recipe_name_label = tk.Label(header_frame, text=recipe['name'], font=("Arial", 14, "bold"),
                                   bg=self.bg_color, fg=self.text_fg)
        recipe_name_label.pack(anchor="w")
        
        ingredients_frame = tk.Frame(ingredients_window, bg=self.bg_color)
        ingredients_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.rowconfigure(0, weight=1)
        
        ingredients_text = tk.Text(ingredients_frame, wrap='word', font=("Arial", 11),
                                 bg=self.text_bg, fg=self.text_fg, relief=tk.FLAT)
        ingredients_text.grid(row=0, column=0, sticky="nsew")
        
        ingredients_scrollbar = tk.Scrollbar(ingredients_frame, command=ingredients_text.yview)
        ingredients_scrollbar.grid(row=0, column=1, sticky="ns")
        ingredients_text.config(yscrollcommand=ingredients_scrollbar.set)
        
        ingredients_text.insert(tk.END, recipe['ingredients'])
        ingredients_text.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(ingredients_window, bg=self.bg_color)
        button_frame.grid(row=2, column=0, pady=10)
        
        close_button = tk.Button(button_frame, text="Close", command=ingredients_window.destroy,
                               width=10, font=("Arial", 10), bg=self.accent_color, fg="white",
                               activebackground=self.highlight_color, activeforeground="white",
                               relief=tk.FLAT, padx=10, pady=5)
        close_button.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = CookingApp(root)
    root.mainloop()