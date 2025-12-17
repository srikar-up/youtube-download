import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import download_range_func
import threading
import os
import sys
import datetime
from ctypes import windll, byref, sizeof, c_int

# --- CONFIGURATION ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

# --- Define custom colors ---
RED_NORMAL = "#E53E3E"
RED_HOVER = "#C53030"
RED_DARK  = "#9B2C2C" 

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("600x680") # Adjusted height
        self.resizable(False, False)
        
        self.video_duration = 0 

        # --- SET RED TITLE BAR (Windows 11) ---
        try:
            self.update() 
            hwnd = windll.user32.GetParent(self.winfo_id())
            # Color 0x003E3EE5 is the BGR hex for #E53E3E
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x003E3EE5)), sizeof(c_int))
        except Exception:
            pass

        # --- UI Elements ---

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.pack(pady=(20, 0))
        
        self.url_entry = ctk.CTkEntry(self, width=500, 
                                      placeholder_text="Enter YouTube video URL here",
                                      border_color=RED_NORMAL,
                                      fg_color="transparent",
                                      placeholder_text_color="gray")
        self.url_entry.pack(pady=5, padx=50, fill='x')

        # Folder Button
        self.folder_button = ctk.CTkButton(self, text="Choose Folder", command=self.choose_folder,
                                           fg_color=RED_NORMAL, hover_color=RED_HOVER)
        self.folder_button.pack(pady=5)
        self.folder_label = ctk.CTkLabel(self, text="Default: Downloads folder")
        self.folder_label.pack()

        # --- Options Frame ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=50, fill="x")

        # Download Type
        self.download_type_label = ctk.CTkLabel(self.options_frame, text="Download Type:")
        self.download_type_label.pack(pady=(5, 0))
        
        self.download_type_var = ctk.StringVar(value="Video + Audio")
        self.download_type_menu = ctk.CTkSegmentedButton(self.options_frame, 
                                                         values=["Video + Audio", "Video Only", "Audio Only"],
                                                         variable=self.download_type_var,
                                                         command=self.update_quality_options,
                                                         selected_color=RED_NORMAL,
                                                         selected_hover_color=RED_HOVER,
                                                         unselected_hover_color=RED_DARK)
        self.download_type_menu.pack(pady=5, padx=20, fill="x")

        # Quality Option
        self.quality_label = ctk.CTkLabel(self.options_frame, text="Select Quality:")
        self.quality_label.pack(pady=(5, 0))
        
        self.quality_var = ctk.StringVar() 
        self.quality_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.quality_var,
                                              values=[],
                                              fg_color=RED_NORMAL,
                                              button_color=RED_NORMAL,
                                              button_hover_color=RED_HOVER,
                                              dropdown_hover_color=RED_HOVER)
        self.quality_menu.pack(pady=5, padx=20, fill="x")

        # --- Clipping Options Frame ---
        self.clip_frame = ctk.CTkFrame(self)
        self.clip_frame.pack(pady=10, padx=50, fill="x")

        self.use_clip_var = ctk.BooleanVar(value=False)
        self.clip_checkbox = ctk.CTkCheckBox(self.clip_frame, text="Enable Video Clipping", 
                                             variable=self.use_clip_var, 
                                             command=self.toggle_clip_inputs,
                                             fg_color=RED_NORMAL, hover_color=RED_HOVER)
        self.clip_checkbox.pack(pady=10)

        # Get Info Button
        self.get_info_button = ctk.CTkButton(self.clip_frame, text="Get Video Length (Enable Sliders)", 
                                             command=self.fetch_video_info,
                                             state="disabled",
                                             fg_color="#444444", hover_color="#333333")
        self.get_info_button.pack(pady=5)

        # Sliders Frame
        self.sliders_frame = ctk.CTkFrame(self.clip_frame, fg_color="transparent")
        
        # Start Slider
        self.start_slider_label = ctk.CTkLabel(self.sliders_frame, text="Start Point")
        self.start_slider_label.grid(row=0, column=0, padx=5, sticky="w")
        self.start_slider = ctk.CTkSlider(self.sliders_frame, from_=0, to=100, number_of_steps=100, 
                                          command=self.on_start_slide, 
                                          progress_color=RED_NORMAL, 
                                          button_color=RED_NORMAL, 
                                          button_hover_color=RED_HOVER)
        self.start_slider.set(0)
        self.start_slider.grid(row=0, column=1, padx=5, sticky="ew")

        # End Slider
        self.end_slider_label = ctk.CTkLabel(self.sliders_frame, text="End Point")
        self.end_slider_label.grid(row=1, column=0, padx=5, sticky="w")
        self.end_slider = ctk.CTkSlider(self.sliders_frame, from_=0, to=100, number_of_steps=100, 
                                        command=self.on_end_slide, 
                                        progress_color=RED_NORMAL, 
                                        button_color=RED_NORMAL, 
                                        button_hover_color=RED_HOVER)
        self.end_slider.set(100)
        self.end_slider.grid(row=1, column=1, padx=5, sticky="ew")
        
        # Time Text Inputs
        self.time_input_frame = ctk.CTkFrame(self.clip_frame, fg_color="transparent")
        self.time_input_frame.pack(pady=10)

        self.start_time_entry = ctk.CTkEntry(self.time_input_frame, width=100, 
                                             placeholder_text="00:00:00",
                                             border_color=RED_NORMAL)
        self.start_time_entry.grid(row=0, column=0, padx=5)
        
        self.lbl_to = ctk.CTkLabel(self.time_input_frame, text="to")
        self.lbl_to.grid(row=0, column=1, padx=5)
        
        self.end_time_entry = ctk.CTkEntry(self.time_input_frame, width=100, 
                                           placeholder_text="00:00:10",
                                           border_color=RED_NORMAL)
        self.end_time_entry.grid(row=0, column=2, padx=5)

        self.toggle_clip_inputs() 

        # --- End Options ---

        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download,
                                           fg_color=RED_NORMAL, hover_color=RED_HOVER)
        self.download_button.pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, mode='indeterminate',
                                           progress_color=RED_NORMAL)
        self.progress.pack(fill='x', padx=50, pady=10)

        # Status
        self.status = ctk.CTkLabel(self, text="Ready")
        self.status.pack(pady=5)

        # --- Initial Setup ---
        self.output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.folder_label.configure(text=f"Folder: {self.output_folder}")
        self.update_quality_options() 

    def toggle_clip_inputs(self):
        """Enables/Disables time entries and buttons based on checkbox."""
        if self.use_clip_var.get():
            self.start_time_entry.configure(state="normal")
            self.end_time_entry.configure(state="normal")
            self.get_info_button.configure(state="normal", fg_color="#555555")
        else:
            self.start_time_entry.configure(state="disabled")
            self.end_time_entry.configure(state="disabled")
            self.get_info_button.configure(state="disabled", fg_color="#333333")
            self.sliders_frame.pack_forget()

    def fetch_video_info(self):
        """Fetches video duration to set up sliders."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL first.")
            return
        
        self.status.configure(text="Fetching video info...")
        self.get_info_button.configure(state="disabled", text="Loading...")
        
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                
            self.after(0, self.setup_sliders, duration)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Could not fetch info: {e}"))
            self.after(0, lambda: self.status.configure(text="Error fetching info"))
        finally:
             self.after(0, lambda: self.get_info_button.configure(state="normal", text="Get Video Length (Refresh)"))

    def setup_sliders(self, duration):
        """Configures sliders with the correct video duration."""
        self.video_duration = duration
        self.status.configure(text=f"Video length: {self.format_seconds(duration)}")
        
        self.sliders_frame.pack(pady=5, after=self.get_info_button)
        self.start_slider.configure(to=duration, number_of_steps=duration)
        self.end_slider.configure(to=duration, number_of_steps=duration)
        self.start_slider.set(0)
        self.end_slider.set(duration)
        self.on_start_slide(0)
        self.on_end_slide(duration)

    def on_start_slide(self, value):
        val = int(value)
        if val > self.end_slider.get():
            self.start_slider.set(self.end_slider.get())
            val = int(self.end_slider.get())
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, self.format_seconds(val))

    def on_end_slide(self, value):
        val = int(value)
        if val < self.start_slider.get():
            self.end_slider.set(self.start_slider.get())
            val = int(self.start_slider.get())
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, self.format_seconds(val))

    def format_seconds(self, seconds):
        return str(datetime.timedelta(seconds=int(seconds)))

    def parse_time(self, time_str):
        try:
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 1: return parts[0]
            if len(parts) == 2: return parts[0] * 60 + parts[1]
            if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
            return None
        except ValueError:
            return None

    def update_quality_options(self, value=None):
        download_type = self.download_type_var.get()
        if "Video" in download_type:
            options = ["2160 (4K)", "1440 (2K)", "1080 (HD)", "720 (HD)", "best (Highest)"]
            self.quality_menu.configure(values=options)
            self.quality_var.set("2160 (4K)")
        elif "Audio" in download_type:
            options = ["MP3 - 320k (Best)", "MP3 - 192k (High)", "MP3 - 128k (Medium)", "M4A - Best (Recommended)"]
            self.quality_menu.configure(values=options)
            self.quality_var.set("M4A - Best (Recommended)")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.folder_label.configure(text=f"Folder: {self.output_folder}")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        start_sec = None
        end_sec = None

        if self.use_clip_var.get():
            s_str = self.start_time_entry.get().strip()
            e_str = self.end_time_entry.get().strip()
            start_sec = self.parse_time(s_str)
            end_sec = self.parse_time(e_str)

            if start_sec is None or end_sec is None:
                messagebox.showerror("Error", "Invalid Time Format.")
                return
            if start_sec >= end_sec:
                messagebox.showerror("Error", "End time must be greater than Start time.")
                return

        self.download_button.configure(state="disabled")
        threading.Thread(target=self.download_video, args=(url, start_sec, end_sec), daemon=True).start()

    def download_video(self, url, start_sec, end_sec):
        self.after(0, self.progress.start)
        self.after(0, lambda: self.status.configure(text="Initializing download..."))

        download_type = self.download_type_var.get()
        quality_str = self.quality_var.get()

        if getattr(sys, 'frozen', False):
            script_dir = sys._MEIPASS
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        ffmpeg_path = os.path.join(script_dir, "ffmpeg.exe")
        
        ydl_opts = {
            'quiet': True,
            'noprogress': True,
            'progress_hooks': [self.progress_hook],
        }

        if start_sec is not None and end_sec is not None:
            ydl_opts['download_ranges'] = download_range_func(None, [(start_sec, end_sec)])
            ydl_opts['force_keyframes_at_cuts'] = True 
        
        if os.path.exists(ffmpeg_path):
            ydl_opts['ffmpeg_location'] = ffmpeg_path
            
        postprocessors = []

        try:
            if "Video" in download_type:
                quality = quality_str.split()[0]
                if quality == "best":
                    video_format = "bestvideo"
                else:
                    video_format = f"bestvideo[height<={quality}]"

                if download_type == "Video + Audio":
                    ydl_opts['format'] = f"{video_format}+bestaudio/best"
                    ydl_opts['merge_output_format'] = 'mp4'
                else:
                    ydl_opts['format'] = f"{video_format}/bestvideo"
                
                ydl_opts['outtmpl'] = os.path.join(self.output_folder, '%(title)s.%(ext)s')

            elif "Audio" in download_type:
                ydl_opts['format'] = 'bestaudio/best'
                if "MP3" in quality_str:
                    codec = 'mp3'
                    audio_quality = '320' if "320k" in quality_str else '192' if "192k" in quality_str else '128'
                    ydl_opts['outtmpl'] = os.path.join(self.output_folder, '%(title)s.mp3')
                elif "M4A" in quality_str:
                    codec = 'm4a'
                    audio_quality = '192' 
                    ydl_opts['outtmpl'] = os.path.join(self.output_folder, '%(title)s.m4a')

                postprocessors.append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': codec,
                    'preferredquality': audio_quality,
                })
                ydl_opts['postprocessors'] = postprocessors

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self.on_download_finished, True, None)

        except Exception as e:
            e_msg = "FFmpeg error" if "ffmpeg" in str(e).lower() else str(e)
            self.after(0, self.on_download_finished, False, e_msg)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            if percent:
                self.after(0, lambda: self.status.configure(text=f"Downloading... {percent}"))
        elif d['status'] == 'finished':
            msg = "Converting audio..." if 'postprocessor' in d.get('info_dict', {}).get('filepath', '') else "Processing clip..."
            self.after(0, lambda: self.status.configure(text=msg))

    def on_download_finished(self, success, error_message):
        self.progress.stop()
        self.download_button.configure(state="normal")
        if success:
            self.status.configure(text="Download Complete!")
            messagebox.showinfo("Success", f"Download complete!\nSaved to: {self.output_folder}")
        else:
            self.status.configure(text="Error")
            messagebox.showerror("Error", f"Download failed:\n{error_message}")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
