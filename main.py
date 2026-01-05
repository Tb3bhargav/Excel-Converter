import sys
import subprocess
import importlib
import tkinter as tk
from tkinter import messagebox

def install_dependencies():
    """Checks for required packages and installs them if missing."""
    required = {'pandas', 'openpyxl'}
    missing = set()
    
    for pkg in required:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.add(pkg)
            
    if missing:
        # Create a simple root window to show the message
        root = tk.Tk()
        root.withdraw() # Hide the main window
        
        msg = f"Missing dependencies: {', '.join(missing)}.\nClick OK to install them automatically.\nThis might take a moment."
        if messagebox.askokcancel("Install Dependencies", msg):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                messagebox.showinfo("Success", "Dependencies installed successfully! Starting app...")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to install dependencies.\nError: {e}")
                sys.exit(1)
        else:
            sys.exit(0)
        root.destroy()

def main():
    # 1. Check dependencies
    install_dependencies()
    
    # 2. Import app components (delayed import after installation)
    try:
        from gui import ConverterApp
    except ImportError as e:
        # This might happen if installation failed but didn't throw, or other errors
        print(f"Critical Error: {e}")
        return

    # 3. Start GUI
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
