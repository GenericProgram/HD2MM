import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from backend import ModManagerBackend
from PIL import Image
from tkinterdnd2 import TkinterDnD, DND_FILES

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class HD2ModManager(Tk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="#0b0c10")
        
        self.backend = ModManagerBackend()

        self.title("Helldivers 2 Mod Manager")
        
        # Calculate dynamic window size based on screen resolution
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w = int(screen_w * 0.6)
        h = int(screen_h * 0.7)
        self.geometry(f"{w}x{h}")
        
        # OS Drag and Drop registration
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # UI Elements
        # Game Directory Selection
        self.dir_label = ctk.CTkLabel(self, text="Game Directory:")
        self.dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.dir_entry = ctk.CTkEntry(self, placeholder_text="Path to Helldivers 2 folder...")
        self.dir_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.dir_entry.insert(0, self.backend.game_dir)
        self.dir_entry.configure(state="readonly")
        
        self.browse_btn = ctk.CTkButton(self, text="Browse", command=self.browse_directory)
        self.browse_btn.grid(row=0, column=2, padx=(0, 10), pady=10)

        # Mods List
        self.mods_label = ctk.CTkLabel(self, text="Installed Mods:")
        self.mods_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Scrollable frame for mods
        self.mods_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.mods_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="nsew")

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.btn_frame.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_columnconfigure(1, weight=1)

        self.add_mod_btn = ctk.CTkButton(self.btn_frame, text="Add Mod File(s)", command=self.add_mod)
        self.add_mod_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.refresh_btn = ctk.CTkButton(self.btn_frame, text="Refresh List", command=self.refresh_mods)
        self.refresh_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.deploy_btn = ctk.CTkButton(self.btn_frame, text="Deploy Mods", command=self.deploy_mods, fg_color="green", hover_color="darkgreen")
        self.deploy_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.refresh_mods()

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Helldivers 2 Game Directory")
        if directory:
            if not os.path.exists(os.path.join(directory, "data")):
                messagebox.showwarning("Warning", "The selected directory does not seem to contain a 'data' folder.")
            
            self.backend.set_game_dir(directory)
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, self.backend.game_dir)
            self.dir_entry.configure(state="readonly")
            self.refresh_mods()

    def refresh_mods(self):
        for widget in self.mods_frame.winfo_children():
            widget.destroy()
            
        self.backend.load_scraped_mods()
        scraped_mods = self.backend.scraped_mods
        self.mod_frames = []

        if not scraped_mods:
            lbl = ctk.CTkLabel(self.mods_frame, text="No mods found in testmods directory.")
            lbl.pack(pady=20)
            return

        self.option_var_refs = {}

        for i, mod in enumerate(scraped_mods):
            mod_frame = ctk.CTkFrame(self.mods_frame, fg_color="transparent")
            mod_frame.pack(fill="x", padx=5, pady=2)
            self.mod_frames.append(mod_frame)
            
            # Info sub-frame (matches HD2 Arsenal row)
            info_frame = ctk.CTkFrame(mod_frame, fg_color="#121212", corner_radius=0)
            info_frame.pack(fill="x", padx=0, pady=0)
            info_frame.grid_columnconfigure(2, weight=1)
            
            # Col 0: Drag Handle & Number
            drag_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            drag_frame.grid(row=0, column=0, rowspan=2, padx=(15, 5), pady=10)
            
            drag_lbl = ctk.CTkLabel(drag_frame, text="◯", font=ctk.CTkFont(size=16), text_color="#555", cursor="hand2")
            drag_lbl.pack(side="left", padx=(0, 5))
            
            num_lbl = ctk.CTkLabel(drag_frame, text=str(i + 1), font=ctk.CTkFont(size=14, weight="bold"), text_color="#ccc")
            num_lbl.pack(side="left")
            mod_frame.num_lbl = num_lbl

            # Col 1: Thumbnail with dynamic border
            thumb_frame = ctk.CTkFrame(info_frame, fg_color="transparent", border_width=2, border_color="#333", corner_radius=8)
            thumb_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
            
            if mod["thumbnail_path"]:
                try:
                    img = Image.open(mod["thumbnail_path"])
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(48, 48))
                    img_lbl = ctk.CTkLabel(thumb_frame, image=ctk_img, text="")
                    img_lbl.pack(padx=2, pady=2)
                except Exception:
                    img_lbl = ctk.CTkLabel(thumb_frame, text="NO\nIMAGE", width=48, height=48, font=ctk.CTkFont(size=10))
                    img_lbl.pack(padx=2, pady=2)
            else:
                img_lbl = ctk.CTkLabel(thumb_frame, text="NO\nIMAGE", width=48, height=48, font=ctk.CTkFont(size=10))
                img_lbl.pack(padx=2, pady=2)

            # Col 2: Title and Description
            text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            text_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)
            
            name_lbl = ctk.CTkLabel(text_frame, text=f"☐ {mod['name']}", font=ctk.CTkFont(family="Consolas", size=15, weight="bold"), text_color="#aaa")
            name_lbl.pack(anchor="w")
            
            desc_lbl = ctk.CTkLabel(text_frame, text=mod["description"], font=ctk.CTkFont(family="Consolas", size=12, slant="italic"), text_color="#888", justify="left")
            desc_lbl.pack(anchor="w", pady=(2, 0), fill="x", expand=True)
            
            def on_text_frame_config(event, lbl=desc_lbl):
                if event.width > 20:
                    lbl.configure(wraplength=event.width - 10)
            text_frame.bind("<Configure>", on_text_frame_config)

            # Col 3: Master Switch
            if mod.get("options") and len(mod["options"]) > 1:
                active_count = sum(1 for opt in mod["options"] if opt["name"] in self.backend.active_mods.get(mod["id"], []))
                is_active = (active_count == len(mod["options"]) and active_count > 0)
            else:
                opt_name = mod["options"][0]["name"] if mod.get("options") else ""
                is_active = opt_name in self.backend.active_mods.get(mod["id"], [])
                
            master_var = tk.BooleanVar(value=is_active)
            
            def on_master_toggle(m_id=mod["id"], opts=mod.get("options", []), m_var=master_var):
                is_on = m_var.get()
                for j, opt in enumerate(opts):
                    opt_n = opt["name"]
                    self.backend.toggle_mod_option(m_id, opt_n, is_on)
                    if m_id in self.option_var_refs and j < len(self.option_var_refs[m_id]):
                        self.option_var_refs[m_id][j].set(is_on)
                
            master_switch = ctk.CTkSwitch(info_frame, text="", variable=master_var, command=on_master_toggle, 
                                          progress_color="#00ff00", button_color="#ffffff", button_hover_color="#dddddd", switch_width=40, switch_height=20)
            master_switch.grid(row=0, column=3, rowspan=2, padx=15, pady=10)
            
            def update_visuals(*args, tf=thumb_frame, nl=name_lbl, m=mod, mv=master_var):
                if mv.get():
                    tf.configure(border_color="#00ff00")
                    nl.configure(text=f"☑ {m['name']}", text_color="#ffffff")
                else:
                    tf.configure(border_color="#333")
                    nl.configure(text=f"☐ {m['name']}", text_color="#aaaaaa")
            master_var.trace_add("write", update_visuals)
            update_visuals() # initial state

            # Bind drag events
            for w in [info_frame, drag_frame, drag_lbl, num_lbl, text_frame, name_lbl, desc_lbl]:
                w.bind("<ButtonPress-1>", lambda event, idx=i: self.drag_start(event, idx))
                w.bind("<B1-Motion>", self.drag_motion)
                w.bind("<ButtonRelease-1>", lambda event, idx=i: self.drag_stop(event, idx))

            # Col 4 & 5: Options (⚙) and Menu (⋮)
            options_frame = ctk.CTkFrame(mod_frame, fg_color="#1a1a1a")
            self.option_var_refs[mod["id"]] = []
            
            if mod.get("options") and len(mod["options"]) > 1:
                opt_btn = ctk.CTkButton(info_frame, text="⚙", width=30, height=30, fg_color="transparent", hover_color="#333", text_color="#fff", font=ctk.CTkFont(size=18))
                opt_btn.grid(row=0, column=4, rowspan=2, padx=5, pady=10)
                
                for j, opt in enumerate(mod["options"]):
                    opt_n = opt["name"]
                    var = tk.BooleanVar(value=opt_n in self.backend.active_mods.get(mod["id"], []))
                    self.option_var_refs[mod["id"]].append(var)
                    
                    def ind_toggle(m_id=mod["id"], n=opt_n, v=var):
                        self.backend.toggle_mod_option(m_id, n, v.get())
                        
                    chk = ctk.CTkSwitch(options_frame, text=opt_n, variable=var, command=ind_toggle, progress_color="#00aa00")
                    chk.pack(anchor="w", padx=45, pady=5)
                    
                def toggle_options(frame=options_frame):
                    if frame.winfo_ismapped():
                        frame.pack_forget()
                    else:
                        frame.pack(fill="x", padx=0, pady=(0, 2))
                        
                opt_btn.configure(command=toggle_options)
            elif mod.get("options"):
                # Track single option so master works
                var = tk.BooleanVar(value=master_var.get())
                self.option_var_refs[mod["id"]].append(var)
                
            del_btn = ctk.CTkButton(info_frame, text="⋮", width=20, height=30, fg_color="transparent", hover_color="#333", text_color="#fff", font=ctk.CTkFont(size=18), command=lambda m_id=mod["id"]: self.delete_mod(m_id))
            del_btn.grid(row=0, column=5, rowspan=2, padx=(5, 15), pady=10)

    def drag_start(self, event, idx):
        self.drag_start_idx = idx
        self.current_drag_idx = idx
        self.drag_window = tk.Toplevel(self)
        self.drag_window.overrideredirect(True)
        self.drag_window.attributes('-alpha', 0.8)
        
        mod = self.backend.scraped_mods[idx]
        lbl = ctk.CTkLabel(self.drag_window, text=mod["name"], font=ctk.CTkFont(size=14, weight="bold"), fg_color="#444", padx=10, pady=10)
        lbl.pack()
        
        x = self.mod_frames[idx].winfo_rootx()
        self.drag_window.geometry(f"+{x}+{event.y_root - 20}")

    def drag_motion(self, event):
        if hasattr(self, 'drag_window') and self.drag_window:
            x = self.mod_frames[self.current_drag_idx].winfo_rootx()
            self.drag_window.geometry(f"+{x}+{event.y_root - 20}")
            
            y = event.y_root
            new_idx = self.current_drag_idx
            
            for i, frame in enumerate(self.mod_frames):
                if i == self.current_drag_idx:
                    continue
                try:
                    frame_top = frame.winfo_rooty()
                    frame_bottom = frame_top + frame.winfo_height()
                    if frame_top <= y <= frame_bottom:
                        new_idx = i
                        break
                except Exception:
                    pass
                    
            if new_idx != self.current_drag_idx:
                self.backend.reorder_mod(self.current_drag_idx, new_idx)
                
                mod_frame = self.mod_frames.pop(self.current_drag_idx)
                self.mod_frames.insert(new_idx, mod_frame)
                
                for frame in self.mod_frames:
                    frame.pack_forget()
                for j, frame in enumerate(self.mod_frames):
                    frame.pack(fill="x", padx=5, pady=2)
                    if hasattr(frame, 'num_lbl'):
                        frame.num_lbl.configure(text=str(j + 1))
                    
                self.current_drag_idx = new_idx

    def drag_stop(self, event, start_idx):
        if hasattr(self, 'drag_window') and self.drag_window:
            self.drag_window.destroy()
            self.drag_window = None
            
        self.refresh_mods()

    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        added = 0
        for f in files:
            if f.lower().endswith('.zip'):
                success, msg = self.backend.install_mod_from_zip(f)
                if success:
                    added += 1
                else:
                    messagebox.showerror("Install Error", msg)
        if added > 0:
            self.refresh_mods()
            messagebox.showinfo("Success", f"Installed {added} mod(s) successfully.")

    def add_mod(self):
        if not self.backend.game_dir:
            messagebox.showwarning("Warning", "Please select the game directory first.")
            return
            
        file_paths = filedialog.askopenfilenames(title="Select Mod File(s)")
        if file_paths:
            added = 0
            for file_path in file_paths:
                success, msg = self.backend.add_mod(file_path, overwrite=False)
                if not success:
                    response = messagebox.askyesno("File Exists", f"{msg}. Overwrite?")
                    if response:
                        try:
                            self.backend.add_mod(file_path, overwrite=True)
                            added += 1
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to copy:\n{e}")
                else:
                    added += 1
                    
            if added > 0:
                self.refresh_mods()
                messagebox.showinfo("Success", f"Added {added} mod(s) successfully.")

    def deploy_mods(self):
        try:
            conflicts = self.backend.deploy_mods()
            if conflicts:
                msg = "Mods deployed with conflicts:\n"
                for conflict in conflicts:
                    msg += f"- {conflict[0]}: {conflict[1]} vs {conflict[2]}\n"
                messagebox.showwarning("Deployed with Conflicts", msg)
            else:
                messagebox.showinfo("Success", "Mods staged and deployed successfully!")
        except Exception as e:
            messagebox.showerror("Deploy Error", f"Failed to deploy mods:\n{e}")

    def toggle_mod(self, mod_filename, currently_active):
        pass # Now handled by individual checkboxes

    def delete_mod(self, mod_filename):
        response = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {mod_filename}?")
        if response:
            try:
                mod_path = os.path.join(self.backend.mods_dir, mod_filename)
                if os.path.exists(mod_path):
                    import shutil
                    shutil.rmtree(mod_path)
                self.refresh_mods()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete mod:\n{e}")
