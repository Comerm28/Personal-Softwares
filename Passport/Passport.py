import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from PIL import Image, ImageTk

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}


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
        self.data_path = os.path.join("Passport", "places.json")
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

    # ---------- UI skeleton ----------
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
            command=self.open_edit_window,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=4,
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            btns,
            text="Show Gallery",
            command=self.open_gallery_selected,
            bg="#666666",
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
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._update_preview_for_selection())

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

    # ---------- data ----------
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
        for p in sorted(
            self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True
        ):
            name = p.get("name", "(unnamed)")
            date_str = p.get("date_visited", "")
            display_date = "No Date"
            if date_str:
                try:
                    display_date = datetime.strptime(date_str, "%Y-%m").strftime("%B %Y")
                except ValueError:
                    display_date = date_str
            display = f"{display_date}  —  {name}"
            self.listbox.insert(tk.END, display)

    # ---------- list actions ----------
    def open_add_window(self):
        self.open_edit_window()

    def open_edit_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a place to edit.")
            return
        idx = sel[0]
        target = sorted(
            self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True
        )[idx]
        self.open_edit_window(target)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a place to delete.")
            return
        idx = sel[0]
        sorted_places = sorted(
            self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True
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

    # ---------- gallery ----------
    def open_gallery_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a place to view its gallery.")
            return
        idx = sel[0]
        place = sorted(self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True)[idx]
        photo_dir = place.get("photo_dir")
        if not photo_dir or not os.path.isdir(photo_dir):
            messagebox.showerror("Error", f"The photo directory is invalid or not set.\nPath: {photo_dir}")
            return
        self.show_gallery_window(place, photo_dir)

    def _list_images(self, dir_path):
        try:
            files = sorted(os.listdir(dir_path))
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read folder:\n{e}")
            return []
        out = []
        for f in files:
            p = os.path.join(dir_path, f)
            if os.path.isfile(p) and os.path.splitext(f.lower())[1] in IMAGE_EXTS:
                out.append(p)
        return out

    def _make_scrollable(self, parent):
        canvas = tk.Canvas(parent, highlightthickness=0, bg=self.bg_color)
        vscroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)

        def on_cfg(event):
            canvas.itemconfig(frame_id, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_cfg)
        canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        return frame

    def _show_image_viewer(self, parent, paths, start_idx=0):
        win = tk.Toplevel(parent)
        win.title("Viewer")
        win.geometry("900x700")
        win.configure(bg=self.bg_color)

        idx = {"i": start_idx}
        img_label = ttk.Label(win)
        img_label.pack(fill="both", expand=True)
        caption = ttk.Label(win, anchor="center")
        caption.pack(side="bottom", fill="x")

        cache = {"img": None}

        def show(i):
            if not paths:
                return
            i %= len(paths)
            idx["i"] = i
            p = paths[i]
            try:
                im = Image.open(p)
                w = win.winfo_width() or 900
                h = win.winfo_height() or 700
                im.thumbnail((w - 40, h - 120))
                cache["img"] = ImageTk.PhotoImage(im)
                img_label.configure(image=cache["img"])
                caption.configure(text=f"{os.path.basename(p)}   [{i+1}/{len(paths)}]")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open image:\n{p}\n{e}")

        def prev_():
            show(idx["i"] - 1)

        def next_():
            show(idx["i"] + 1)

        nav = ttk.Frame(win)
        nav.pack(side="bottom", pady=6)
        ttk.Button(nav, text="Prev", command=prev_).pack(side="left", padx=4)
        ttk.Button(nav, text="Next", command=next_).pack(side="left", padx=4)
        win.bind("<Left>", lambda e: prev_())
        win.bind("<Right>", lambda e: next_())
        win.bind("<Configure>", lambda e: show(idx["i"]))
        show(start_idx)

    def show_gallery_window(self, place, directory, thumb_size=(200, 200), columns=4):
        paths = self._list_images(directory)
        if not paths:
            messagebox.showinfo("Gallery", "No images found.")
            return

        gallery_win = tk.Toplevel(self.root)
        gallery_win.title(f"Gallery — {place.get('name','')}")
        gallery_win.geometry("900x700")
        gallery_win.configure(bg=self.bg_color)

        container = ttk.Frame(gallery_win)
        container.pack(fill="both", expand=True)
        grid_frame = self._make_scrollable(container)

        thumbs = []

        def open_view(i):
            self._show_image_viewer(gallery_win, paths, i)

        for i, p in enumerate(paths):
            try:
                im = Image.open(p)
                im.thumbnail(thumb_size)
                tkimg = ImageTk.PhotoImage(im)
            except Exception:
                continue
            thumbs.append(tkimg)
            cell = ttk.Frame(grid_frame, padding=6, borderwidth=1, relief="solid")
            r, c = divmod(i, columns)
            cell.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            lbl = ttk.Label(cell, image=tkimg)
            lbl.pack()
            cap = ttk.Label(cell, text=os.path.basename(p), width=30)
            cap.pack()
            lbl.bind("<Button-1>", lambda e, i=i: open_view(i))
            cap.bind("<Button-1>", lambda e, i=i: open_view(i))

        footer = ttk.Frame(gallery_win)
        footer.pack(fill="x")
        ttk.Label(footer, text=f"{len(paths)} images").pack(side="left", padx=8)
        ttk.Button(
            footer,
            text="Open Folder",
            command=lambda: self._open_folder(directory),
        ).pack(side="right", padx=8)

    def _open_folder(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.run(["open", path])
            else:
                import subprocess
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

    # ---------- details ----------
    def open_details_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        target = sorted(
            self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True
        )[idx]
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

    # ---------- editor ----------
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

        date_frame = tk.Frame(w, bg=self.bg_color)
        date_frame.pack(fill=tk.X, padx=12, pady=(6, 0))
        tk.Label(
            date_frame,
            text="Date Visited (YYYY-MM):",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        date_ent = tk.Entry(
            date_frame, bg=self.text_bg, fg=self.text_fg, font=("Arial", 11)
        )
        date_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        if is_edit:
            date_ent.insert(0, place.get("date_visited", ""))

        photo_dir_frame = tk.Frame(w, bg=self.bg_color)
        photo_dir_frame.pack(fill=tk.X, padx=12, pady=(6, 0))
        tk.Label(
            photo_dir_frame,
            text="Photo Directory:",
            bg=self.bg_color,
            fg=self.text_fg,
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        photo_dir_ent = tk.Entry(
            photo_dir_frame, bg=self.text_bg, fg=self.text_fg, font=("Arial", 11)
        )
        photo_dir_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        def pick_dir():
            d = filedialog.askdirectory()
            if d:
                photo_dir_ent.delete(0, tk.END)
                photo_dir_ent.insert(0, d)

        ttk.Button(photo_dir_frame, text="Browse", command=pick_dir).pack(side=tk.LEFT, padx=6)

        if is_edit:
            photo_dir_ent.insert(0, place.get("photo_dir", ""))

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
            date_visited = date_ent.get().strip()
            photo_dir = photo_dir_ent.get().strip()
            scores = {c: int(vars_map[c].get()) for c in self.categories}
            overall = self.compute_overall(scores)
            entry = {
                "id": (place.get("id") if is_edit else f"{name}_{datetime.now().timestamp()}"),
                "name": name,
                "country": country,
                "date_visited": date_visited,
                "photo_dir": photo_dir,
                "scores": scores,
                "overall": overall,
                "notes": notes_txt.get(1.0, tk.END).strip(),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

    # ---------- preview ----------
    def _update_preview_for_selection(self):
        sel = self.listbox.curselection()
        if not sel:
            self.preview.config(state=tk.NORMAL)
            self.preview.delete(1.0, tk.END)
            self.preview.config(state=tk.DISABLED)
            return
        idx = sel[0]
        p = sorted(
            self.places, key=lambda x: x.get("date_visited", "0000-00"), reverse=True
        )[idx]
        date_str = p.get("date_visited", "N/A")
        display_date = date_str
        if date_str != "N/A":
            try:
                display_date = datetime.strptime(date_str, "%Y-%m").strftime("%B %Y")
            except ValueError:
                display_date = date_str
        lines = [
            f"Name: {p.get('name')}",
            f"Country: {p.get('country','')}",
            f"Date Visited: {display_date}",
            f"Overall: {p.get('overall'):.1f}",
            f"Photo Directory: {p.get('photo_dir', 'N/A')}",
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
    root.mainloop()


if __name__ == "__main__":
    main()
