import customtkinter as ctk
from gui import HD2ModManager

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = HD2ModManager()
    app.mainloop()
