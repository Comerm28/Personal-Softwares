import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class ShowRankerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Show Ranker")
        self.root.geometry("900x600")
        self.bg_color = "#2d2d2d"
        self.text_bg = "#3d3d3d"
        self.text_fg = "#ffffff"
        self.accent_color = "#ff6b35"
        self.highlight_color = "#ff8c69"
        self.data_path = os.path.join("Show Ranker", "shows.json")
        self.categories = [
            "fights",
            "animation",
            "themes",
            "deaths",
            "shenanigans",
            "main character",
            "side characters",
            "power system",
            "story",
            "pace",
            "rewatchability",
            "world building",
            "consistency",
            "aura farming",
            "meaning",
        ]
        self.shows = self.load_shows()
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

        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(main_frame, bg=self.bg_color)
        header.pack(fill=tk.X, pady=8, padx=10)
        title = tk.Label(
            header,
            text="Show Ranker",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_fg,
        )
        title.pack(side=tk.LEFT)

        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side=tk.RIGHT)
        add_btn = tk.Button(
            btn_frame,
            text="Add Show",
            command=self.open_add_window,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        add_btn.pack(side=tk.LEFT, padx=4)
        edit_btn = tk.Button(
            btn_frame,
            text="Edit Selected",
            command=self.open_edit_selected,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        edit_btn.pack(side=tk.LEFT, padx=4)
        delete_btn = tk.Button(
            btn_frame,
            text="Delete",
            command=self.delete_selected,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        delete_btn.pack(side=tk.LEFT, padx=4)

        body = tk.Frame(main_frame, bg=self.bg_color)
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

        scrollbar = tk.Scrollbar(body, command=self.listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        right_panel = tk.Frame(body, width=320, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        info_label = tk.Label(
            right_panel,
            text="Details / Preview",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 12, "bold"),
        )
        info_label.pack(anchor="nw", pady=(0, 6))
        self.preview_text = tk.Text(
            right_panel,
            bg=self.text_bg,
            fg=self.text_fg,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Arial", 10),
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_listbox()

    def compute_overall(self, scores: dict) -> float:
        if not scores:
            return 0.0
        vals = [max(0, min(100, int(scores.get(cat, 0)))) for cat in self.categories]
        return round(sum(vals) / len(self.categories), 1)

    def load_shows(self):
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

    def save_shows(self):
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.shows, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for show in sorted(self.shows, key=lambda s: s.get("overall", 0), reverse=True):
            name = show.get("name", "(untitled)")
            overall = show.get("overall", 0)
            self.listbox.insert(tk.END, f"{overall:5.1f}  —  {name}")

    def open_add_window(self):
        self.open_edit_window()

    def open_edit_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a show to edit.")
            return
        idx = sel[0]
        current = sorted(self.shows, key=lambda s: s.get("overall", 0), reverse=True)[
            idx
        ]
        self.open_edit_window(current)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a show to delete.")
            return
        idx = sel[0]
        sorted_shows = sorted(
            self.shows, key=lambda s: s.get("overall", 0), reverse=True
        )
        target = sorted_shows[idx]
        confirm = messagebox.askyesno("Delete", f"Delete '{target.get('name')}'?")
        if not confirm:
            return
        for i, s in enumerate(self.shows):
            if s.get("id") == target.get("id"):
                del self.shows[i]
                break
        self.save_shows()
        self.refresh_listbox()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def open_details_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        sorted_shows = sorted(
            self.shows, key=lambda s: s.get("overall", 0), reverse=True
        )
        target = sorted_shows[idx]
        self.show_details_window(target)

    def show_details_window(self, show):
        w = tk.Toplevel(self.root)
        w.title(show.get("name", "Details"))
        w.geometry("640x520")
        w.configure(bg=self.bg_color)
        header = tk.Label(
            w,
            text=f"{show.get('name')}  —  {show.get('overall',0):.1f}",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_fg,
        )
        header.pack(anchor="w", padx=12, pady=(12, 6))
        info_frame = tk.Frame(w, bg=self.bg_color)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        left = tk.Frame(info_frame, bg=self.bg_color)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = tk.Frame(info_frame, bg=self.bg_color)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        scores_text = tk.Text(
            left,
            bg=self.text_bg,
            fg=self.text_fg,
            state=tk.NORMAL,
            wrap=tk.WORD,
            font=("Arial", 10),
        )
        scores_text.pack(fill=tk.BOTH, expand=True)
        lines = []
        for cat in self.categories:
            val = show.get("scores", {}).get(cat, 0)
            lines.append(f"{cat.title():20}: {val:3d}/100")
        scores_text.insert(tk.END, "\n".join(lines))
        scores_text.config(state=tk.DISABLED)
        comments_label = tk.Label(
            right,
            text="Comments",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        )
        comments_label.pack(anchor="nw")
        comments_text = tk.Text(
            right, bg=self.text_bg, fg=self.text_fg, width=30, height=10, wrap=tk.WORD
        )
        comments_text.pack(fill=tk.BOTH, expand=True)
        comments_text.insert(tk.END, show.get("comments", ""))
        comments_text.config(state=tk.DISABLED)
        btn_frame = tk.Frame(w, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(6, 12))
        edit_btn = tk.Button(
            btn_frame,
            text="Edit",
            command=lambda: (w.destroy(), self.open_edit_window(show)),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        edit_btn.pack(side=tk.RIGHT, padx=10)
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=w.destroy,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        )
        close_btn.pack(side=tk.RIGHT)

    def open_edit_window(self, show=None):
        is_edit = show is not None
        w = tk.Toplevel(self.root)
        w.title("Edit Show" if is_edit else "Add Show")
        w.geometry("760x640")
        w.configure(bg=self.bg_color)

        name_frame = tk.Frame(w, bg=self.bg_color)
        name_frame.pack(fill=tk.X, padx=12, pady=(12, 6))
        tk.Label(
            name_frame,
            text="Show Name:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        name_entry = tk.Entry(
            name_frame, bg=self.text_bg, fg=self.text_fg, font=("Arial", 11)
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        if is_edit:
            name_entry.insert(0, show.get("name", ""))

        scores_frame = tk.Frame(w, bg=self.bg_color)
        scores_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 0))
        canvas = tk.Canvas(scores_frame, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(scores_frame, command=canvas.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        canvas.configure(yscrollcommand=sb.set)
        inner = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_config(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", on_config)

        score_vars = {}
        for i, cat in enumerate(self.categories):
            row = tk.Frame(inner, bg=self.bg_color)
            row.pack(fill=tk.X, pady=4)
            tk.Label(
                row,
                text=cat.title() + ":",
                width=18,
                anchor="w",
                bg=self.bg_color,
                fg=self.text_fg,
                font=("Arial", 10),
            ).pack(side=tk.LEFT)
            sv = tk.IntVar(value=show.get("scores", {}).get(cat, 50) if is_edit else 50)
            spin = tk.Spinbox(
                row,
                from_=0,
                to=100,
                textvariable=sv,
                width=6,
                bg=self.text_bg,
                fg=self.text_fg,
                relief=tk.FLAT,
            )
            spin.pack(side=tk.LEFT, padx=(6, 0))
            score_vars[cat] = sv

        comments_frame = tk.Frame(w, bg=self.bg_color)
        comments_frame.pack(fill=tk.BOTH, padx=12, pady=(6, 0))
        tk.Label(
            comments_frame,
            text="Comments:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        comments_text = tk.Text(
            comments_frame,
            height=8,
            bg=self.text_bg,
            fg=self.text_fg,
            font=("Arial", 10),
        )
        comments_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        if is_edit:
            comments_text.insert(tk.END, show.get("comments", ""))

        def on_save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing name", "Please enter a show name.")
                return
            scores = {cat: int(score_vars[cat].get()) for cat in self.categories}
            overall = self.compute_overall(scores)
            entry = {
                "id": (
                    show.get("id")
                    if is_edit
                    else f"{name}_{datetime.now().timestamp()}"
                ),
                "name": name,
                "scores": scores,
                "overall": overall,
                "comments": comments_text.get(1.0, tk.END).strip(),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if is_edit:
                for i, s in enumerate(self.shows):
                    if s.get("id") == show.get("id"):
                        self.shows[i] = entry
                        break
            else:
                self.shows.append(entry)
            self.save_shows()
            self.refresh_listbox()
            w.destroy()

        save_btn = tk.Button(
            w,
            text="Save",
            command=on_save,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
        )
        save_btn.pack(side=tk.RIGHT, padx=12, pady=12)
        cancel_btn = tk.Button(
            w,
            text="Cancel",
            command=w.destroy,
            bg="#666666",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
        )
        cancel_btn.pack(side=tk.RIGHT, pady=12)

    def _update_preview_for_selection(self):
        sel = self.listbox.curselection()
        if not sel:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.config(state=tk.DISABLED)
            return
        idx = sel[0]
        sorted_shows = sorted(
            self.shows, key=lambda s: s.get("overall", 0), reverse=True
        )
        s = sorted_shows[idx]
        lines = [
            f"Name: {s.get('name')}",
            f"Overall: {s.get('overall'):.1f}",
            "",
            "Scores:",
        ]
        for cat in self.categories:
            lines.append(f"  {cat.title():18}: {s.get('scores',{}).get(cat,0):3d}")
        lines.append("")
        lines.append("Comments:")
        lines.append(s.get("comments", ""))
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "\n".join(lines))
        self.preview_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ShowRankerApp(root)
    app.listbox.bind("<<ListboxSelect>>", lambda e: app._update_preview_for_selection())
    root.mainloop()


if __name__ == "__main__":
    main()
