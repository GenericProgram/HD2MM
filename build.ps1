echo "Building HD2MM Executable..."
.\venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed --collect-all customtkinter --collect-all tkinterdnd2 main.py
echo "Build complete. Check the 'dist/main' folder for the executable."
