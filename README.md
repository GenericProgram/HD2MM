# 🚀 HD2MM - Helldivers 2 Mod Manager

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![UI](https://img.shields.io/badge/UI-CustomTkinter-orange)

HD2MM is a simple, highly lightweight, and user-friendly GUI mod manager for Helldivers 2. Built with Python, it focuses on providing a fast and clean experience to manage your game modifications seamlessly. The tool was created by Gemini 3.1 Pro using Antigravity IDE.

## ✨ Features

- **🪶 Extremely Lightweight**: Designed with simplicity in mind to run quickly without bloating your system.
- **📜 Script Mod Support**: Fully supports a variety of mod types, making it easy for users to utilize and toggle script mods.
- **🔄 Toggle Mods on the Fly**: Quickly enable or disable mods with a single click (automatically appending `.disabled` to safely hide them from the game).
- **📁 Easy Installation**: Simply select mod files through the UI to copy them straight into your Helldivers 2 `data` directory.
- **🌙 Modern Interface**: Enjoy a sleek, dark-themed UI out of the box using `CustomTkinter`.

## 🛠️ Setup & Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/GenericProgram/HD2MM.git
   cd HD2MM/HD2MM
   ```

2. Set up a Python virtual environment:
   ```powershell
   python -m venv venv
   ```

3. Install the dependencies:
   ```powershell
   .\venv\Scripts\pip install -r requirements.txt
   ```

## 🎮 How to Use

1. **Launch the app**:
   ```powershell
   .\venv\Scripts\python.exe main.py
   ```
2. **Select Game Directory**: Click **Browse** and select your main Helldivers 2 installation directory. The tool will automatically locate your `data` folder.
3. **Install Mods**: Click **Add Mod File(s)** to import your files (such as `.patch_0` files or script mod files).
4. **Manage Mods**: Use the interface to **Enable**, **Disable**, or **Delete** your installed modifications easily.

---
**Disclaimer**: This project is not officially affiliated with Arrowhead Game Studios or Sony Interactive Entertainment. Use mods at your own risk!
