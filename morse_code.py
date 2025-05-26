import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import numpy as np
from datetime import datetime
import pygame
import json
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import sys
from pathlib import Path
from PIL import Image, ImageTk
import unittest
from unittest.mock import patch
import io
import tempfile
import zipfile
import shutil
from packaging import version

# --- Constants ---
APP_NAME = "🏛️ Ancient Morse Oracle 🏛️"
VERSION = "1.0.0"
AUTHOR = "Lefa Jele-Masemola"
WELCOME_MESSAGE = (
    "Hearken, seeker of the ancient dots and dashes!\n"
    "The Oracle shall translate thy mortal words to the divine language of Morse,\n"
    "and reveal the hidden meanings within the sacred signals..."
)

# Morse Code Dictionary (expanded with ancient symbols)
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--', 
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', 
    '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', 
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', 
    ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', 
    '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/',
    'Æ': '.-.-', 'Ø': '---.', 'Å': '.--.-', 'ß': '...--..', 'Ç': '-.-..',
    'Ñ': '--.--', '§': '-.-.-', '¿': '..-.-', '¡': '--...-'
}

REVERSE_MORSE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}

# --- Audio Engine ---
class MorseAudio:
    def __init__(self):
        pygame.mixer.init()
        self.dot_sound = self._generate_sound(800, 100)
        self.dash_sound = self._generate_sound(800, 300)
        self.space_sound = self._generate_sound(0, 100)
        self.playing = False
    
    def _generate_sound(self, frequency, duration):
        sample_rate = 44100
        samples = int(sample_rate * duration / 1000.0)
        buf = np.zeros((samples, 2), dtype=np.int16)
        if frequency > 0:
            for s in range(samples):
                t = float(s) / sample_rate
                buf[s][0] = int(32767.0 * np.sin(2.0 * np.pi * frequency * t))
                buf[s][1] = int(32767.0 * np.sin(2.0 * np.pi * frequency * t))
        return pygame.sndarray.make_sound(buf)
    
    def play_morse(self, code):
        if self.playing:
            return
            
        self.playing = True
        for char in code:
            if char == '.':
                self.dot_sound.play()
                pygame.time.delay(150)
            elif char == '-':
                self.dash_sound.play()
                pygame.time.delay(350)
            elif char == ' ':
                pygame.time.delay(250)
            elif char == '/':
                pygame.time.delay(500)
        self.playing = False

# --- Ancient Theme System ---
class AncientThemes:
    def __init__(self):
        self.themes = {
            "Stone Tablet": {
                "bg": "#2E2A27",
                "fg": "#D4C8BE",
                "text_bg": "#3A3632",
                "text_fg": "#E8E0D8",
                "button_bg": "#4A4238",
                "button_fg": "#F0E8E0",
                "active_bg": "#5A5248",
                "insert_bg": "#E8B060",
                "select_bg": "#806040"
            },
            "Papyrus Scroll": {
                "bg": "#F5ECD7",
                "fg": "#3A2E18",
                "text_bg": "#FFF8E8",
                "text_fg": "#2A1E08",
                "button_bg": "#D8C8A8",
                "button_fg": "#2A1E08",
                "active_bg": "#E8D8B8",
                "insert_bg": "#A08040",
                "select_bg": "#C0A060"
            },
            "Obsidian Mirror": {
                "bg": "#0A0A12",
                "fg": "#A0A0C0",
                "text_bg": "#101018",
                "text_fg": "#C0C0E0",
                "button_bg": "#202030",
                "button_fg": "#D0D0F0",
                "active_bg": "#303040",
                "insert_bg": "#6060C0",
                "select_bg": "#404080"
            }
        }
        self.current_theme = "Stone Tablet"
    
    def get_theme(self, name=None):
        return self.themes.get(name or self.current_theme, self.themes["Stone Tablet"])

# --- Core Translation Functions ---
def letters_to_morse(text):
    """Convert text to Morse code with ancient symbols support"""
    morse = []
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            morse.append(MORSE_CODE_DICT[char])
        elif char == '\n':
            morse.append('/')
        else:
            morse.append('�')  # Unknown character symbol
    return ' '.join(morse)

def morse_to_letters(code):
    """Convert Morse code to text with error handling"""
    words = code.split(' / ')
    decoded = []
    for word in words:
        letters = word.split()
        dec_word = []
        for letter in letters:
            if letter in REVERSE_MORSE_DICT:
                dec_word.append(REVERSE_MORSE_DICT[letter])
            else:
                dec_word.append('�')  # Unknown Morse symbol
        decoded.append(''.join(dec_word))
    return ' '.join(decoded)

# --- Main Application ---
class AncientMorseOracle:
    def __init__(self, root):
        self.root = root
        self.audio_enabled = True
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("900x700")
        self.root.minsize(1000, 800)
        
        # Initialize subsystems
        self.audio = MorseAudio()
        self.themes = AncientThemes()
        self.history = []
        self.current_file = None
        
       
        style = ttk.Style()
        style.configure('Output.TLabelframe', background='#f0f0f0')
        
        # Load ancient icon
        self._load_icons()
        
        # Setup UI
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()
        self._apply_theme()
        
        # Display welcome message
        self._show_welcome_message()
        
        # Initialize audio (lazy load)
        self.audio_enabled = True
    
    def _load_icons(self):
        """Load ancient-style icons for the UI"""
        try:
            # Try to load from embedded resources
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "assets", "oracle_icon.png")
            
            if os.path.exists(icon_path):
                self.icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, self.icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
    
    def _create_menu(self):
        """Create the ancient oracle menu system"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Translation", command=self._new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._confirm_exit, accelerator="Alt+F4")
        menubar.add_cascade(label="Scrolls", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self._cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All", command=self._clear_all, accelerator="Ctrl+Del")
        menubar.add_cascade(label="Engrave", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=self.themes.current_theme)
        for theme_name in self.themes.themes:
            view_menu.add_radiobutton(
                label=theme_name,
                variable=self.theme_var,
                value=theme_name,
                command=self._change_theme
            )
        menubar.add_cascade(label="Visions", menu=view_menu)
        
        # Audio menu
        audio_menu = tk.Menu(menubar, tearoff=0)
        audio_menu.add_command(
            label="Play Morse Code", 
            command=self._play_current_morse,
            accelerator="Ctrl+P"
        )
        audio_menu.add_command(
            label="Stop Playing", 
            command=self._stop_audio,
            accelerator="Ctrl+Shift+P"
        )
        menubar.add_cascade(label="Echoes", menu=audio_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Oracle Guide", command=self._show_help)
        help_menu.add_command(label="Morse Reference", command=self._show_reference)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Wisdom", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self._save_file_as())
        self.root.bind("<Control-p>", lambda e: self._play_current_morse())
        self.root.bind("<Control-Shift-p>", lambda e: self._stop_audio())
    
    def _create_main_frame(self):
        """Create the main application frame with all widgets"""
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with ancient decoration
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.rowconfigure(0, weight=0)
        main_frame.columnconfigure(0, weight=1)
    
        self.title_label = ttk.Label(
            title_frame,
            text=APP_NAME,
            font=("Palatino", 24, "bold"),
            anchor=tk.CENTER
        )
        self.title_label.pack(fill=tk.X)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Decipher the Language of the Ancients",
            font=("Palatino", 12),
            anchor=tk.CENTER
        )
        subtitle_label.pack(fill=tk.X)
        
        # Mode selection with ancient radio buttons
        mode_frame = ttk.LabelFrame(main_frame, text=" Direction of Prophecy ", padding=10)
        mode_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        main_frame.rowconfigure(1, weight=0)

        
        self.mode_var = tk.StringVar(value="encode")
        
        ttk.Radiobutton(
            mode_frame,
            text="Words to Morse (Encode)",
            variable=self.mode_var,
            value="encode",
            command=self._update_ui_mode
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            mode_frame,
            text="Morse to Words (Decode)",
            variable=self.mode_var,
            value="decode",
            command=self._update_ui_mode
        ).pack(side=tk.LEFT, padx=10)
        
        # Input area
        input_frame = ttk.LabelFrame(main_frame, text=" Inscribe Thy Message ", padding=10)
        #input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        input_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.rowconfigure(2, weight=1)  # Give input area some weight
    
        self.input_label = ttk.Label(
            input_frame,
            text="Inscribe Thy Message",  
            font=("Segoe UI", 10, "bold")
        )
        self.input_label.pack(anchor="w", pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Courier New", 12),
            undo=True,
            maxundo=100
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        #button_frame.pack(fill=tk.X, pady=5)
        main_frame.rowconfigure(3, weight=0)
        
        ttk.Button(
            button_frame,
            text="Consult the Oracle",
            command=self._translate,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Hear the Echoes",
            command=self._play_current_morse,
            state=tk.NORMAL if self.audio_enabled else tk.DISABLED
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear Tablets",
            command=self._clear_all
        ).pack(side=tk.RIGHT, padx=5)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text=" Oracle's Revelation ", padding=10)
        #output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        output_frame = ttk.LabelFrame(main_frame, text=" Oracle's Revelation ", padding=10)
        output_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.rowconfigure(4, weight=3)  # Giving output area most of the space!
        
        self.output_label = ttk.Label(
        output_frame,
        text="Oracle's Revelation",
        font=("Segoe UI", 10, "bold")
    )
        self.output_label.pack(anchor="w", pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Courier New", 18),
            state=tk.NORMAL,
            height=30,
            width=100,
            bg="#f8f8f8",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.output_text.insert(tk.END, "Translation will appear here...")
        self.output_text.config(state=tk.DISABLED) 
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
        #self.output_text.pack(fill=tk.X, expand=False, ipady=100)
    
    def _create_status_bar(self):
        """Create the status bar at bottom of window"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to decipher...")
        
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=1, pady=1)
        
        ttk.Label(
            status_bar,
            textvariable=self.status_var,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            status_bar,
            text=f"v{VERSION}",
            anchor=tk.E
        ).pack(side=tk.RIGHT, padx=5)
    
    def _apply_theme(self, theme_name=None):
        """Apply the selected ancient theme"""
        theme = self.themes.get_theme(theme_name)
        
        # Main window
        self.root.config(bg=theme["bg"])
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')  # Most customizable base theme
        
        # Configure colors
        style.configure('.', background=theme["bg"], foreground=theme["fg"])
        style.configure('TFrame', background=theme["bg"])
        style.configure('TLabel', background=theme["bg"], foreground=theme["fg"])
        style.configure('TButton', 
                      background=theme["button_bg"],
                      foreground=theme["button_fg"],
                      bordercolor=theme["button_bg"],
                      lightcolor=theme["button_bg"],
                      darkcolor=theme["button_bg"])
        style.map('TButton',
                 background=[('active', theme["active_bg"])])
        
        # Special accent button style
        style.configure('Accent.TButton',
                      background="#8B4513",  # SaddleBrown
                      foreground="#F5DEB3",  # Wheat
                      font=('Helvetica', 10, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', "#A0522D")])  # Sienna
        
        # Text widgets
        self.input_text.config(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["insert_bg"],
            selectbackground=theme["select_bg"]
        )
        self.output_text.config(
            bg=theme["text_bg"],
            fg=theme["text_fg"],
            insertbackground=theme["insert_bg"],
            selectbackground=theme["select_bg"],
            font=("Courier New", 14)  # Consistent larger font
        )
        
        # Label frames
        style.configure('TLabelframe',
                      background=theme["bg"],
                      foreground=theme["fg"])
        style.configure('TLabelframe.Label',
                      background=theme["bg"],
                      foreground=theme["fg"])
    
    def _update_ui_mode(self):
        """Update UI when translation mode changes"""
        if self.mode_var.get() == "encode":
            self.input_label.config(text="Inscribe Thy Message")
            self.output_label.config(text="Oracle's Morse Revelation")
        else:
            self.input_label.config(text="Inscribe Morse Code")
            self.output_label.config(text="Oracle's Deciphered Words")
    
    def _translate(self):
        """Perform the translation based on current mode"""
        input_text = self.input_text.get("1.0", tk.END).strip()
        
        if not input_text:
            self.status_var.set("The Oracle requires input to translate!")
            return
        
        try:
            if self.mode_var.get() == "encode":
                result = letters_to_morse(input_text)
            else:
                result = morse_to_letters(input_text)
              
            
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
            self.output_text.config(state=tk.DISABLED)
            
            # Add to history
            self.history.append({
                "mode": self.mode_var.get(),
                "input": input_text,
                "output": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            self.status_var.set("The Oracle has spoken!")
        except Exception as e:
            messagebox.showerror(
                "Oracle's Distress",
                f"The sacred symbols confuse the Oracle!\n\n{str(e)}"
            )
            self.status_var.set("Translation failed!")
    
    def _play_current_morse(self):
        """Play the current Morse code as audio"""
        if not self.audio_enabled:
            messagebox.showwarning(
                "Echoes Silenced",
                "The audio features are not available.\n"
                "Install numpy to enable this feature."
            )
            return
        
        if self.mode_var.get() == "decode":
            messagebox.showwarning(
                "Wrong Direction",
                "You must encode text to Morse before playing."
            )
            return
        
        morse_code = self.output_text.get("1.0", tk.END).strip()
        if not morse_code:
            messagebox.showwarning(
                "Silent Oracle",
                "No Morse code to play. Perform a translation first."
            )
            return
        
        self.audio.play_morse(morse_code)
        self.status_var.set("The echoes of Morse code fill the chamber...")
    
    def _stop_audio(self):
        """Stop any currently playing audio"""
        pygame.mixer.stop()
        self.status_var.set("The echoes fade to silence...")
    
    def _new_file(self):
        """Start a new translation"""
        if self._check_unsaved_changes():
            self.input_text.delete("1.0", tk.END)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.config(state=tk.DISABLED)
            self.current_file = None
            self.status_var.set("New tablet prepared...")
    
    def _open_file(self):
        """Open a saved translation file"""
        if self._check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                title="Open Sacred Scroll",
                filetypes=[
                    ("Oracle Files", "*.mor"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert(tk.END, data.get("input", ""))
                    
                    self.output_text.config(state=tk.NORMAL)
                    self.output_text.delete("1.0", tk.END)
                    self.output_text.insert(tk.END, data.get("output", ""))
                    self.output_text.config(state=tk.DISABLED)
                    
                    self.mode_var.set(data.get("mode", "encode"))
                    self.current_file = file_path
                    
                    self.status_var.set(f"Opened: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror(
                        "Scroll Corrupted",
                        f"The sacred scroll could not be read!\n\n{str(e)}"
                    )
    
    def _save_file(self):
        """Save the current translation"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self._save_file_as()
    
    def _save_file_as(self):
        """Save the current translation with a new filename"""
        file_path = filedialog.asksaveasfilename(
            title="Preserve the Oracle's Words",
            defaultextension=".mor",
            filetypes=[
                ("Oracle Files", "*.mor"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
    
    def _save_to_file(self, file_path):
        """Save data to specified file"""
        data = {
            "input": self.input_text.get("1.0", tk.END).strip(),
            "output": self.output_text.get("1.0", tk.END).strip(),
            "mode": self.mode_var.get(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": VERSION
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.status_var.set(f"Preserved: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            messagebox.showerror(
                "Preservation Failed",
                f"The Oracle's words could not be preserved!\n\n{str(e)}"
            )
            return False
    
    def _check_unsaved_changes(self):
        """Check for unsaved changes and prompt to save"""
        input_text = self.input_text.get("1.0", tk.END).strip()
        output_text = self.output_text.get("1.0", tk.END).strip()
        
        if input_text or output_text:
            response = messagebox.askyesnocancel(
                "Unsaved Prophecies",
                "You have unsaved translations. Preserve them for posterity?"
            )
            
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                return self._save_file()
        
        return True
    
    def _clear_all(self):
        """Clear both input and output"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Tablets wiped clean...")
    
    def _cut(self):
        """Cut selected text"""
        self.input_text.event_generate("<<Cut>>")
    
    def _copy(self):
        """Copy selected text"""
        if self.input_text.tag_ranges(tk.SEL):
            self.input_text.event_generate("<<Copy>>")
        else:
            self.output_text.event_generate("<<Copy>>")
    
    def _paste(self):
        """Paste from clipboard"""
        self.input_text.event_generate("<<Paste>>")
    
    def _change_theme(self):
        """Change the application theme"""
        self.themes.current_theme = self.theme_var.get()
        self._apply_theme()
        self.status_var.set(f"Vision changed to {self.themes.current_theme}...")
    
    def _show_welcome_message(self):
        """Display welcome message in output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, WELCOME_MESSAGE)
        self.output_text.config(state=tk.DISABLED)
    
    def _show_help(self):
        """Show help dialog"""
        help_text = (
            "ORACLE'S GUIDE TO THE SACRED DOTS AND DASHES\n\n"
            "1. Choose your direction:\n"
            "   - Words to Morse: Translate normal text to Morse code\n"
            "   - Morse to Words: Decipher Morse code back to text\n\n"
            "2. Inscribe your message in the upper tablet\n"
            "3. Click 'Consult the Oracle' to perform the translation\n"
            "4. The revelation will appear in the lower tablet\n\n"
            "ADDITIONAL POWERS:\n"
            "- Hear the Echoes: Play Morse code as sound\n"
            "- Preserve Scrolls: Save your translations\n"
            "- Visions: Change the appearance of the Oracle\n\n"
            "May the spirits of Morse and Vail guide your path!"
        )
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Oracle's Guide")
        help_window.geometry("600x400")
        
        text = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=("Palatino", 12),
            padx=10,
            pady=10
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(
            help_window,
            text="Acknowledge",
            command=help_window.destroy
        ).pack(pady=10)
    
    def _show_reference(self):
        """Show Morse code reference chart"""
        reference_window = tk.Toplevel(self.root)
        reference_window.title("Sacred Symbols Reference")
        reference_window.geometry("500x600")
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(reference_window)
        scrollbar = ttk.Scrollbar(reference_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add reference content
        ttk.Label(
            scrollable_frame,
            text="SACRED MORSE SYMBOLS",
            font=("Palatino", 16, "bold")
        ).pack(pady=10)
        
        # Letters
        ttk.Label(
            scrollable_frame,
            text="Letters:",
            font=("Palatino", 12, "underline")
        ).pack(anchor=tk.W, padx=10)
        
        letters_frame = ttk.Frame(scrollable_frame)
        letters_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i, (char, code) in enumerate(sorted(MORSE_CODE_DICT.items())):
            if char.isalpha():
                if i % 6 == 0 and i != 0:
                    letters_frame = ttk.Frame(scrollable_frame)
                    letters_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(
                    letters_frame,
                    text=f"{char}: {code}",
                    width=10
                ).pack(side=tk.LEFT, padx=5)
        
        # Numbers
        ttk.Label(
            scrollable_frame,
            text="Numbers:",
            font=("Palatino", 12, "underline")
        ).pack(anchor=tk.W, padx=10, pady=(10,0))
        
        numbers_frame = ttk.Frame(scrollable_frame)
        numbers_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i in range(10):
            ttk.Label(
                numbers_frame,
                text=f"{i}: {MORSE_CODE_DICT[str(i)]}",
                width=10
            ).pack(side=tk.LEFT, padx=5)
        
        # Punctuation
        ttk.Label(
            scrollable_frame,
            text="Punctuation:",
            font=("Palatino", 12, "underline")
        ).pack(anchor=tk.W, padx=10, pady=(10,0))
        
        punct_frame = ttk.Frame(scrollable_frame)
        punct_frame.pack(fill=tk.X, padx=10, pady=5)
        
        punct_items = [(k,v) for k,v in MORSE_CODE_DICT.items() if not (k.isalnum() or k == ' ')]
        
        for i, (char, code) in enumerate(punct_items):
            if i % 4 == 0 and i != 0:
                punct_frame = ttk.Frame(scrollable_frame)
                punct_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                punct_frame,
                text=f"{char}: {code}",
                width=15
            ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            scrollable_frame,
            text="Close",
            command=reference_window.destroy
        ).pack(pady=10)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = (
            f"{APP_NAME} v{VERSION}\n\n"
            "A mystical tool for communing with the ancient\n"
            "language of dots and dashes, used by oracles\n"
            "and telegraphic mystics throughout the ages.\n\n"
            f"Consecrated by: {AUTHOR}\n\n"
            "May your messages travel swiftly through\n"
            "the aether as did those of old..."
        )
        
        messagebox.showinfo("About the Oracle", about_text)
    
    def _confirm_exit(self):
        """Confirm before exiting application"""
        if self._check_unsaved_changes():
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._confirm_exit)
        self.root.mainloop()

# --- Packaging Support ---
def create_windows_installer():
    """Create a Windows installer using PyInstaller"""
    try:
        import PyInstaller.__main__
        
        print("Creating Windows executable...")
        
        # Create a temporary directory for build files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy assets
            assets_dir = os.path.join(temp_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)
            
            # Copy icon file if exists
            if os.path.exists("assets/oracle_icon.png"):
                shutil.copy("assets/oracle_icon.png", assets_dir)
            
            # Prepare PyInstaller command
            pyinstaller_args = [
                '--name=AncientMorseOracle',
                '--onefile',
                '--windowed',
                '--add-data=assets;assets',
                '--icon=assets/oracle_icon.ico',
                'morse_oracle.py'
            ]
            
            PyInstaller.__main__.run(pyinstaller_args)
            
            print("Executable created in dist/ directory")
    except ImportError:
        print("PyInstaller not found. Install with: pip install pyinstaller")

# --- Unit Tests ---
class TestAncientMorseOracle(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = AncientMorseOracle(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
    def test_letters_to_morse(self):
        self.assertEqual(letters_to_morse("SOS"), "... --- ...")
        self.assertEqual(letters_to_morse("Hello 123"), ".... . .-.. .-.. --- / .---- ..--- ...--")
    
    def test_morse_to_letters(self):
        self.assertEqual(morse_to_letters("... --- ..."), "SOS")
        self.assertEqual(morse_to_letters(".... . .-.. .-.. --- / .---- ..--- ...--"), "HELLO 123")
    
    def test_unknown_characters(self):
        self.assertEqual(letters_to_morse("π"), "�")
        self.assertEqual(morse_to_letters("........"), "�")
    
    def test_gui_translation(self):
        # Test encode
        self.app.mode_var.set("encode")
        self.app.input_text.insert(tk.END, "TEST")
        self.app._translate()
        output = self.app.output_text.get("1.0", tk.END).strip()
        self.assertEqual(output, "- . ... -")
        
        # Test decode
        self.app._clear_all()
        self.app.mode_var.set("decode")
        self.app.input_text.insert(tk.END, "- . ... -")
        self.app._translate()
        output = self.app.output_text.get("1.0", tk.END).strip()
        self.assertEqual(output, "TEST")

# --- Main Execution ---
if __name__ == "__main__":
    # Check if we're creating an installer
    if len(sys.argv) > 1 and sys.argv[1] == "--create-installer":
        create_windows_installer()
    else:
        # Run the application
        root = tk.Tk()
        app = AncientMorseOracle(root)
        app.run()