import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class PassportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Places I've Been")
        self.root.geometry("900x600")
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#ff6b35"
        self.highlight_color = "#ff8c69"
        self.data_path = os.path.join("Places", "places.json")
        self.categories = [
            "food",
            "scenery",
            "safety",
            "accessibility",
            "value",
            "culture",
            "nightlife",
            "nature",
            "history",
            "comfort",
            "cleanliness",
            "transport",
            "friendliness",
            "weather",
        ]
        self.places = self.load_places()
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TFrame", background=self.bg_color)
        style.configure("TNotebook", background=self.bg_color)
        style.configure(
            "TNotebook.Tab",
            background="#444444",
            foreground="#ffffff",
            padding=[8, 2],
            font=("Arial", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.accent_color), ("!selected", "#444444")],
        )

        main = tk.Frame(self.root, bg=self.bg_color)
        main.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(main, bg=self.bg_color)
        header.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(
            header,
            text="Places I've Been",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_fg,
        ).pack(side=tk.LEFT)

        btns = tk.Frame(header, bg=self.bg_color)
        btns.pack(side=tk.RIGHT)
        tk.Button(
            btns,
            text="Add Place",
            command=self.open_add_window,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            btns,
            text="Edit Selected",
            command=self.open_edit_selected,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            btns,
            text="Delete",
            command=self.delete_selected,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.LEFT, padx=4)

        body = tk.Frame(main, bg=self.bg_color)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.listbox = tk.Listbox(
            body,
            bg=self.text_bg,
            fg=self.text_fg,
            selectbackground=self.accent_color,
            selectforeground="white",
            font=("Arial", 11),
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.open_details_selected())

        sb = tk.Scrollbar(body, command=self.listbox.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)

        right = tk.Frame(body, width=340, bg=self.bg_color)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)
        tk.Label(
            right,
            text="Preview / Details",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 12, "bold"),
        ).pack(anchor="nw", pady=(0, 6))
        self.preview = tk.Text(
            right,
            bg=self.text_bg,
            fg=self.text_fg,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Arial", 10),
        )
        self.preview.pack(fill=tk.BOTH, expand=True)

        self.refresh_listbox()

    def compute_overall(self, scores: dict) -> float:
        if not scores:
            return 0.0
        vals = [max(0, min(100, int(scores.get(c, 0)))) for c in self.categories]
        return round(sum(vals) / len(vals), 1)

    def load_places(self):
        try:
            folder = os.path.dirname(self.data_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)
            if os.path.exists(self.data_path):
                with open(self.data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def save_places(self):
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.places, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in sorted(self.places, key=lambda x: x.get("overall", 0), reverse=True):
            name = p.get("name", "(unnamed)")
            overall = p.get("overall", 0)
            country = p.get("country", "")
            display = f"{overall:5.1f}  —  {name}" + (
                f" ({country})" if country else ""
            )
            self.listbox.insert(tk.END, display)

    def open_add_window(self):
        self.open_edit_window()

    def open_edit_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a place to edit.")
            return
        idx = sel[0]
        target = sorted(self.places, key=lambda x: x.get("overall", 0), reverse=True)[
            idx
        ]
        self.open_edit_window(target)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a place to delete.")
            return
        idx = sel[0]
        sorted_places = sorted(
            self.places, key=lambda x: x.get("overall", 0), reverse=True
        )
        target = sorted_places[idx]
        if not messagebox.askyesno("Delete", f"Delete '{target.get('name')}'?"):
            return
        for i, p in enumerate(self.places):
            if p.get("id") == target.get("id"):
                del self.places[i]
                break
        self.save_places()
        self.refresh_listbox()
        self.preview.config(state=tk.NORMAL)
        self.preview.delete(1.0, tk.END)
        self.preview.config(state=tk.DISABLED)

    def open_details_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        target = sorted(self.places, key=lambda x: x.get("overall", 0), reverse=True)[
            idx
        ]
        self.show_details_window(target)

    def show_details_window(self, place):
        w = tk.Toplevel(self.root)
        w.title(place.get("name", "Details"))
        w.geometry("700x520")
        w.configure(bg=self.bg_color)
        header = tk.Label(
            w,
            text=f"{place.get('name')}  —  {place.get('overall',0):.1f}",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_fg,
        )
        header.pack(anchor="w", padx=12, pady=(12, 6))
        frame = tk.Frame(w, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        left = tk.Frame(frame, bg=self.bg_color)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = tk.Frame(frame, bg=self.bg_color)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        scores = tk.Text(
            left,
            bg=self.text_bg,
            fg=self.text_fg,
            state=tk.NORMAL,
            wrap=tk.WORD,
            font=("Arial", 10),
        )
        scores.pack(fill=tk.BOTH, expand=True)
        lines = []
        for c in self.categories:
            val = place.get("scores", {}).get(c, 0)
            lines.append(f"{c.title():18}: {val:3d}/100")
        scores.insert(tk.END, "\n".join(lines))
        scores.config(state=tk.DISABLED)
        info = tk.Label(
            right,
            text="Notes",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        )
        info.pack(anchor="nw")
        notes = tk.Text(
            right, bg=self.text_bg, fg=self.text_fg, width=32, height=12, wrap=tk.WORD
        )
        notes.pack(fill=tk.BOTH, expand=True)
        notes.insert(tk.END, place.get("notes", ""))
        notes.config(state=tk.DISABLED)
        btns = tk.Frame(w, bg=self.bg_color)
        btns.pack(fill=tk.X, pady=(6, 12))
        tk.Button(
            btns,
            text="Edit",
            command=lambda: (w.destroy(), self.open_edit_window(place)),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.RIGHT, padx=10)
        tk.Button(
            btns,
            text="Close",
            command=w.destroy,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.RIGHT)

    def open_edit_window(self, place=None):
        is_edit = place is not None
        w = tk.Toplevel(self.root)
        w.title("Edit Place" if is_edit else "Add Place")
        w.geometry("760x740")
        w.configure(bg=self.bg_color)

        top = tk.Frame(w, bg=self.bg_color)
        top.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(
            top,
            text="Place Name:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        name_ent = tk.Entry(top, bg=self.text_bg, fg=self.text_fg, font=("Arial", 11))
        name_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        if is_edit:
            name_ent.insert(0, place.get("name", ""))

        country_frame = tk.Frame(w, bg=self.bg_color)
        country_frame.pack(fill=tk.X, padx=12, pady=(6, 0))
        tk.Label(
            country_frame,
            text="Country / Region:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        country_ent = tk.Entry(
            country_frame, bg=self.text_bg, fg=self.text_fg, font=("Arial", 11)
        )
        country_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        if is_edit:
            country_ent.insert(0, place.get("country", ""))

        scores_frame = tk.Frame(w, bg=self.bg_color)
        scores_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 0))
        canvas = tk.Canvas(scores_frame, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(scores_frame, command=canvas.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        canvas.configure(yscrollcommand=sb.set)
        inner = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def oncfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", oncfg)

        vars_map = {}
        for c in self.categories:
            row = tk.Frame(inner, bg=self.bg_color)
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row,
                text=c.title() + ":",
                width=18,
                anchor="w",
                bg=self.bg_color,
                fg=self.text_fg,
                font=("Arial", 10),
            ).pack(side=tk.LEFT)
            iv = tk.IntVar(value=place.get("scores", {}).get(c, 50) if is_edit else 50)
            spin = tk.Spinbox(
                row,
                from_=0,
                to=100,
                textvariable=iv,
                width=6,
                bg=self.text_bg,
                fg=self.text_fg,
                relief=tk.FLAT,
            )
            spin.pack(side=tk.LEFT, padx=(6, 0))
            vars_map[c] = iv

        notes_frame = tk.Frame(w, bg=self.bg_color)
        notes_frame.pack(fill=tk.BOTH, padx=12, pady=(6, 0))
        tk.Label(
            notes_frame,
            text="Notes / Impressions:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        notes_txt = tk.Text(
            notes_frame, height=8, bg=self.text_bg, fg=self.text_fg, font=("Arial", 10)
        )
        notes_txt.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        if is_edit:
            notes_txt.insert(tk.END, place.get("notes", ""))

        def on_save():
            name = name_ent.get().strip()
            if not name:
                messagebox.showwarning("Missing name", "Please enter a place name.")
                return
            country = country_ent.get().strip()
            scores = {c: int(vars_map[c].get()) for c in self.categories}
            overall = self.compute_overall(scores)
            entry = {
                "id": (
                    place.get("id")
                    if is_edit
                    else f"{name}_{datetime.now().timestamp()}"
                ),
                "name": name,
                "country": country,
                "scores": scores,
                "overall": overall,
                "notes": notes_txt.get(1.0, tk.END).strip(),
                "visited": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if is_edit:
                for i, p in enumerate(self.places):
                    if p.get("id") == place.get("id"):
                        self.places[i] = entry
                        break
            else:
                self.places.append(entry)
            self.save_places()
            self.refresh_listbox()
            w.destroy()

        tk.Button(
            w,
            text="Save",
            command=on_save,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
        ).pack(side=tk.RIGHT, padx=12, pady=12)
        tk.Button(
            w,
            text="Cancel",
            command=w.destroy,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
        ).pack(side=tk.RIGHT, pady=12)

    def _update_preview_for_selection(self):
        sel = self.listbox.curselection()
        if not sel:
            self.preview.config(state=tk.NORMAL)
            self.preview.delete(1.0, tk.END)
            self.preview.config(state=tk.DISABLED)
            return
        idx = sel[0]
        p = sorted(self.places, key=lambda x: x.get("overall", 0), reverse=True)[idx]
        lines = [
            f"Name: {p.get('name')}",
            f"Country: {p.get('country','')}",
            f"Overall: {p.get('overall'):.1f}",
            "",
            "Scores:",
        ]
        for c in self.categories:
            lines.append(f"  {c.title():18}: {p.get('scores',{}).get(c,0):3d}")
        lines.append("")
        lines.append("Notes:")
        lines.append(p.get("notes", ""))
        self.preview.config(state=tk.NORMAL)
        self.preview.delete(1.0, tk.END)
        self.preview.insert(tk.END, "\n".join(lines))
        self.preview.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = PassportApp(root)
    app.listbox.bind("<<ListboxSelect>>", lambda e: app._update_preview_for_selection())
    root.mainloop()


if __name__ == "__main__":
    main()
