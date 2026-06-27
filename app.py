import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from gtts import gTTS
import os
import threading
import pygame
import json
import time
from datetime import datetime
from deep_translator import GoogleTranslator

class EnterpriseTranslator:
    def __init__(self, window):
        self.root = window
        self.root.title("CodeAlpha AI Engine — NexusTranslate v1.0")
        self.root.geometry("700x720")
        self.root.configure(bg="#0d1117")
        self.root.resizable(False, False)
        
        pygame.mixer.init()
        self.log_file = "translation_session_log.json"
        
        self.languages = {
            "English": "en", "Hindi": "hi", "Spanish": "es", 
            "French": "fr", "German": "de", "Italian": "it", 
            "Japanese": "ja", "Korean": "ko", "Russian": "ru", 
            "Chinese (Simplified)": "zh-CN"
        }
        
        self.initialize_styles()
        self.assemble_architecture()

    def initialize_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TCombobox", 
                             fieldbackground="#161b22", 
                             background="#21262d", 
                             foreground="#000000", 
                             bordercolor="#30363d",
                             arrowcolor="#58a6ff")
        self.root.option_add("*TCombobox*Listbox.background", "#161b22")
        self.root.option_add("*TCombobox*Listbox.foreground", "#c9d1d9")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#21262d")

    def assemble_architecture(self):
        brand_frame = tk.Frame(self.root, bg="#161b22", height=70, bd=0, highlightbackground="#30363d", highlightthickness=1)
        brand_frame.pack(fill="x", side="top")
        
        brand_label = tk.Label(brand_frame, text="NEXUS TRANSLATE ENGINE", font=("Consolas", 16, "bold"), fg="#58a6ff", bg="#161b22")
        brand_label.pack(pady=10, side="left", padx=30)
        
        status_tag = tk.Label(brand_frame, text="PRODUCTION READY", font=("Arial", 8, "bold"), fg="#238636", bg="#21262d", padx=8, pady=3)
        status_tag.pack(pady=15, side="right", padx=30)

        main_container = tk.Frame(self.root, bg="#0d1117")
        main_container.pack(fill="both", expand=True, padx=40, pady=25)

        io_frame = tk.Frame(main_container, bg="#0d1117")
        io_frame.pack(fill="x", pady=5)

        tk.Label(io_frame, text="SOURCE CONFIG", font=("Consolas", 10, "bold"), fg="#8b949e", bg="#0d1117").grid(row=0, column=0, sticky="w")
        self.src_combo = ttk.Combobox(io_frame, values=list(self.languages.keys()), state="readonly", width=22, font=("Arial", 10, "bold"))
        self.src_combo.set("English")
        self.src_combo.grid(row=1, column=0, pady=5, padx=(0, 20))

        tk.Label(io_frame, text="TARGET CONFIG", font=("Consolas", 10, "bold"), fg="#8b949e", bg="#0d1117").grid(row=0, column=1, sticky="w")
        self.tgt_combo = ttk.Combobox(io_frame, values=list(self.languages.keys()), state="readonly", width=22, font=("Arial", 10, "bold"))
        self.tgt_combo.set("Hindi")
        self.tgt_combo.grid(row=1, column=1, pady=5)

        tk.Label(main_container, text="INPUT TEXT", font=("Consolas", 10, "bold"), fg="#8b949e", bg="#0d1117").pack(anchor="w", pady=(15, 5))
        self.input_text = tk.Text(main_container, height=6, width=70, font=("Segoe UI", 11), bg="#161b22", fg="#c9d1d9", insertbackground="#ffffff", bd=0, highlightbackground="#30363d", highlightthickness=1, padx=12, pady=12)
        self.input_text.pack(fill="x")

        self.action_btn = tk.Button(main_container, text="TRANSLATE NOW", font=("Consolas", 11, "bold"), bg="#238636", fg="#ffffff", activebackground="#2ea44f", activeforeground="#ffffff", bd=0, height=2, cursor="hand2", command=self.trigger_translation)
        self.action_btn.pack(fill="x", pady=20)

        tk.Label(main_container, text="TRANSLATED OUTPUT", font=("Consolas", 10, "bold"), fg="#8b949e", bg="#0d1117").pack(anchor="w", pady=(5, 5))
        self.output_text = tk.Text(main_container, height=6, width=70, font=("Segoe UI", 11), bg="#161b22", fg="#58a6ff", bd=0, highlightbackground="#30363d", highlightthickness=1, padx=12, pady=12, state="disabled")
        self.output_text.pack(fill="x")

        ctrl_frame = tk.Frame(main_container, bg="#0d1117")
        ctrl_frame.pack(fill="x", pady=25)

        self.copy_btn = tk.Button(ctrl_frame, text="📋 Copy Text", font=("Consolas", 10, "bold"), bg="#21262d", fg="#c9d1d9", activebackground="#30363d", activeforeground="#c9d1d9", bd=0, width=22, height=2, cursor="hand2", highlightbackground="#30363d", highlightthickness=1, command=self.copy_output)
        self.copy_btn.grid(row=0, column=0, padx=(0, 15))

        self.audio_btn = tk.Button(ctrl_frame, text="🔊 Listen", font=("Consolas", 10, "bold"), bg="#21262d", fg="#c9d1d9", activebackground="#30363d", activeforeground="#c9d1d9", bd=0, width=22, height=2, cursor="hand2", highlightbackground="#30363d", highlightthickness=1, command=self.execute_audio_thread)
        self.audio_btn.grid(row=0, column=1)

    def log_transaction(self, src, tgt, raw, res):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source_lang": src,
            "target_lang": tgt,
            "input_bytes": len(raw),
            "output_bytes": len(res)
        }
        try:
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            logs.append(log_entry)
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=4)
        except Exception:
            pass

    def run_translation_worker(self, text, src, tgt):
        try:
            result = GoogleTranslator(source=src.lower(), target=tgt.lower()).translate(text)
            
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)
            self.output_text.config(state="disabled")
            
            self.log_transaction(src, tgt, text, result)
        except Exception as e:
            messagebox.showerror("Pipeline Exception", f"Process aborted: {str(e)}")
        finally:
            self.action_btn.config(state="normal", text="TRANSLATE NOW")

    def trigger_translation(self):
        raw_input = self.input_text.get("1.0", tk.END).strip()
        if not raw_input:
            messagebox.showwarning("Validation Error", "Please enter some text to translate!")
            return
        
        self.action_btn.config(state="disabled", text="PROCESSING...")
        threading.Thread(target=self.run_translation_worker, args=(raw_input, self.src_combo.get(), self.tgt_combo.get()), daemon=True).start()

    def copy_output(self):
        data = self.output_text.get("1.0", tk.END).strip()
        if data:
            pyperclip.copy(data)
            messagebox.showinfo("Success", "Text copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "Nothing to copy!")

    def run_audio_engine(self):
        payload = self.output_text.get("1.0", tk.END).strip()
        if not payload:
            messagebox.showwarning("Warning", "No text available to speak!")
            return
        
        try:
            tgt_lang = self.tgt_combo.get()
            iso_code = self.languages.get(tgt_lang, "en")
            cache_file = f"stream_cache_{int(time.time())}.mp3"
            
            tts = gTTS(text=payload, lang=iso_code, slow=False)
            tts.save(cache_file)
            
            pygame.mixer.music.load(cache_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            
            try:
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Audio Error", f"Playback failed: {str(e)}")

    def execute_audio_thread(self):
        threading.Thread(target=self.run_audio_engine, daemon=True).start()

if __name__ == "__main__":
    runtime_instance = tk.Tk()
    engine = EnterpriseTranslator(runtime_instance)
    runtime_instance.mainloop()