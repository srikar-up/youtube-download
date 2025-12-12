import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
from PIL import Image # <-- ADDED IMPORT FOR LOGO

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") # We will override this manually

# --- Define our new red colors ---
RED_NORMAL = "#E53E3E"
RED_HOVER = "#C53030"

class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        # Increased height for the logo
        self.geometry("600x550") 
        self.resizable(False, False)

        # --- (OPTIONAL) SET WINDOW ICON ---
        # 1. Get a .ico file (e.g., "logo.ico") and place it in your folder
        # 2. Uncomment the line below:
        # self.iconbitmap("logo.ico")
        # 3. See the new pyinstaller command at the end.

        # --- (OPTIONAL) ADD IN-APP LOGO ---
        # 1. Get a .png file (e.g., "logo.png") and place it in your folder
        # 2. Uncomment the 3 lines below:
        # self.logo_image = ctk.CTkImage(light_image=Image.open("logo.png"),
        #                                dark_image=Image.open("logo.png"),
        #                                size=(48, 48))
        # self.logo_label = ctk.CTkLabel(self, image=self.logo_image, text="")
        # self.logo_label.pack(pady=(10, 0))


        # --- UI Elements ---

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="YouTube URL:")
        self.url_label.pack(pady=(10, 5)) # Adjusted padding
        self.url_entry = ctk.CTkEntry(self, width=500, placeholder_text="Enter YouTube video URL here")
        self.url_entry.pack(pady=5, padx=50, fill='x')

        # Folder Button
        self.folder_button = ctk.CTkButton(self, text="Choose Folder", command=self.choose_folder,
                                           fg_color=RED_NORMAL, hover_color=RED_HOVER) # <-- Added color
        self.folder_button.pack(pady=5)
        self.folder_label = ctk.CTkLabel(self, text="Default: Downloads folder")
        self.folder_label.pack()

        # --- Options Frame ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=50, fill="x")

        # Download Type Option
        self.download_type_label = ctk.CTkLabel(self.options_frame, text="Download Type:")
        self.download_type_label.pack(pady=(10, 5))
        
        self.download_type_var = ctk.StringVar(value="Video + Audio")
        self.download_type_menu = ctk.CTkSegmentedButton(self.options_frame, 
                                                         values=["Video + Audio", "Video Only", "Audio Only"],
                                                         variable=self.download_type_var,
                                                         command=self.update_quality_options,
                                                         selected_color=RED_NORMAL, # <-- Added color
                                                         selected_hover_color=RED_HOVER) # <-- Added color
        self.download_type_menu.pack(pady=5, padx=20, fill="x")

        # Quality Option
        self.quality_label = ctk.CTkLabel(self.options_frame, text="Select Quality:")
        self.quality_label.pack(pady=(10, 5))
        
        self.quality_var = ctk.StringVar() 
        self.quality_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.quality_var,
                                              values=[],
                                              fg_color=RED_NORMAL, # <-- Added color
                                              button_color=RED_NORMAL, # <-- Added color
                                              button_hover_color=RED_HOVER) # <-- Added color
        self.quality_menu.pack(pady=5, padx=20, fill="x")

        # --- End OptionsFrame ---

        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download,
                                           fg_color=RED_NORMAL, hover_color=RED_HOVER) # <-- Added color
        self.download_button.pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, mode='indeterminate',
                                           progress_color=RED_NORMAL) # <-- Added color
        self.progress.pack(fill='x', padx=50, pady=10)

        # Status
        self.status = ctk.CTkLabel(self, text="Ready")
        self.status.pack(pady=5)

        # --- Initial Setup ---
        self.output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.folder_label.configure(text=f"Folder: {self.output_folder}")
        
        self.update_quality_options() 

    def update_quality_options(self, value=None):
        """Dynamically updates the quality menu based on download type."""
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

        self.download_button.configure(state="disabled")
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        """
        Runs in a background thread. Uses self.after() for all UI updates.
        """
        
        self.after(0, self.progress.start)
        self.after(0, lambda: self.status.configure(text="Initializing download..."))

        download_type = self.download_type_var.get()
        quality_str = self.quality_var.get()

        # --- PYINSTALLER FFmpeg FIX ---
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
                    if "320k" in quality_str: audio_quality = '320'
                    elif "192k" in quality_str: audio_quality = '192'
                    else: audio_quality = '128'
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
            error_str = str(e).lower()
            if "ffmpeg" in error_str or "ffprobe" in error_str:
                e_msg = "FFmpeg error: Could not merge or convert file. Make sure ffmpeg.exe is in the script's folder."
            else:
                e_msg = str(e)
            self.after(0, self.on_download_finished, False, e_msg)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '').strip()
            if percent_str:
                status_text = f"Downloading... {percent_str}"
                self.after(0, lambda: self.status.configure(text=status_text))
        
        elif d['status'] == 'finished':
            if 'postprocessor' in d.get('info_dict', {}).get('filepath', ''):
                 self.after(0, lambda: self.status.configure(text="Converting audio..."))
            else:
                self.after(0, lambda: self.status.configure(text="Finalizing file (merging)..."))

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