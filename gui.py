import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from parser import WhatsAppParser
from chatbot import ChatAnalyzer
from utils import save_to_excel

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AntiGravity WhatsApp → Excel Converter")
        self.root.geometry("700x550")
        
        # State
        self.parser = WhatsAppParser()
        self.analyzer = None
        self.df = None
        self.selected_file = None
        
        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("Accent.TButton", background="#0078d7", foreground="white")
        
        self.setup_ui()

    def setup_ui(self):
        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 1: Converter
        self.tab_converter = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_converter, text='Converter')
        self.setup_converter_tab()

        # Tab 2: Chatbot
        self.tab_chatbot = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chatbot, text='Chat Analysis')
        self.setup_chatbot_tab()
        
        # Footer / Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_converter_tab(self):
        frame = ttk.Frame(self.tab_converter, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Header
        lbl_title = ttk.Label(frame, text="WhatsApp Chat Converter", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=(0, 20))
        
        # File Selection
        self.btn_browse = ttk.Button(frame, text="Browse File (.txt / .zip)", command=self.browse_file)
        self.btn_browse.pack(fill='x', pady=5)
        
        self.lbl_file = ttk.Label(frame, text="No file selected", foreground="gray")
        self.lbl_file.pack(pady=5)
        
        # Convert Button
        self.btn_convert = ttk.Button(frame, text="Convert to Excel", command=self.start_conversion, state='disabled', style="Accent.TButton")
        self.btn_convert.pack(pady=20, fill='x')
        
        # Progress
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=10)
        
        # Instructions
        lbl_instr = ttk.Label(frame, text="Instructions:\n1. Export chat from WhatsApp (without media).\n2. Select the .txt or .zip file.\n3. Click Convert.", justify=tk.LEFT)
        lbl_instr.pack(pady=20, anchor='w')

    def setup_chatbot_tab(self):
        frame = ttk.Frame(self.tab_chatbot, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Chat History
        self.chat_history = tk.Text(frame, state='disabled', wrap='word', height=15)
        self.chat_history.pack(fill='both', expand=True, pady=(0, 10))
        
        # Input Area
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')
        
        self.entry_query = ttk.Entry(input_frame)
        self.entry_query.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.entry_query.bind("<Return>", lambda e: self.ask_chatbot())
        
        self.btn_ask = ttk.Button(input_frame, text="Ask", command=self.ask_chatbot)
        self.btn_ask.pack(side='right')
        
        # Initial Message
        self._append_chat("System", "Please convert a chat file first to enable analysis.\nकृपया विश्लेषण सक्षम करने के लिए पहले चैट फ़ाइल कनवर्ट करें।")

    def browse_file(self):
        filetypes = [("WhatsApp Chat", "*.txt *.zip"), ("Text Files", "*.txt"), ("Zip Files", "*.zip"), ("All Files", "*.*")]
        filename = filedialog.askopenfilename(title="Select WhatsApp Export", filetypes=filetypes)
        if filename:
            self.selected_file = filename
            self.lbl_file.config(text=os.path.basename(filename), foreground="black")
            self.btn_convert.config(state='normal')
            self.status_var.set("File selected. Ready to convert.")

    def start_conversion(self):
        if not self.selected_file:
            return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")])
        if not save_path:
            return
            
        self.btn_convert.config(state='disabled')
        self.btn_browse.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("Converting... Please wait.")
        
        # Run in thread to keep UI responsive
        threading.Thread(target=self.run_conversion, args=(save_path,), daemon=True).start()

    def run_conversion(self, save_path):
        try:
            # Parse
            self.df = self.parser.parse_file(self.selected_file)
            
            # Save
            save_to_excel(self.df, save_path)
            
            # Init Chatbot
            self.analyzer = ChatAnalyzer(self.df)
            
            # Update UI on main thread
            self.root.after(0, self.on_conversion_success, save_path)
            
        except Exception as e:
            self.root.after(0, self.on_conversion_error, str(e))

    def on_conversion_success(self, save_path):
        self.progress.stop()
        self.btn_convert.config(state='normal')
        self.btn_browse.config(state='normal')
        self.status_var.set("Conversion Complete!")
        
        messagebox.showinfo("Success", f"File converted successfully!\nSaved to: {save_path}")
        
        # Switch to Chatbot tab and notify
        self.notebook.select(self.tab_chatbot)
        self._append_chat("System", "Analysis ready! You can ask questions now.\nविश्लेषण तैयार है! अब आप प्रश्न पूछ सकते हैं।")
        
        # AntiGravity Effect (Simple visual cue)
        self.root.attributes('-alpha', 0.95) # Slight transparency for "floating" feel

    def on_conversion_error(self, error_msg):
        self.progress.stop()
        self.btn_convert.config(state='normal')
        self.btn_browse.config(state='normal')
        self.status_var.set("Error occurred.")
        messagebox.showerror("Error", f"Conversion failed:\n{error_msg}")

    def ask_chatbot(self):
        query = self.entry_query.get().strip()
        if not query:
            return
            
        self._append_chat("You", query)
        self.entry_query.delete(0, tk.END)
        
        if self.analyzer:
            response = self.analyzer.get_response(query)
            self._append_chat("Bot", response)
        else:
            self._append_chat("Bot", "Please convert a file first.")

    def _append_chat(self, sender, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
