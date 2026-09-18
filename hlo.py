import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import download_range_func
import threading
import os
import sys
import shutil
import datetime
from ctypes import windll, byref, sizeof, c_int

# --- CONFIGURATION ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Custom Brand Colors ---
RED_NORMAL = "#E53E3E"
RED_HOVER = "#C53030"
RED_DARK = "#9B2C2C"


def find_ffmpeg():
    """Locates ffmpeg.exe from:
    1. Directory of current executable (if frozen with PyInstaller)
    2. PyInstaller extraction folder sys._MEIPASS (if bundled)
    3. Directory containing this script
    4. System PATH (e.g. winget, chocolatey, or manual PATH install)
    """
    # 1 & 2: When packaged as .exe
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        candidate = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.isfile(candidate):
            return candidate

        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            candidate = os.path.join(meipass, "ffmpeg.exe")
            if os.path.isfile(candidate):
                return candidate

    # 3: Next to source script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.isfile(candidate):
        return candidate

    # 4: Check system PATH
    path_bin = shutil.which("ffmpeg")
    if path_bin:
        return path_bin

    return None


class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyRed — YouTube Downloader & Clipper")
        self.geometry("620x700")
        self.resizable(False, False)

        self.video_duration = 0
        self.ffmpeg_path = find_ffmpeg()

        # Apply custom red title bar on Windows 11
        self.after(100, self._apply_windows11_titlebar)

        # Build UI
        self._build_ui()

        # Initial folder & options setup
        self.output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.folder_label.configure(text=f"Save to: {self.output_folder}")
        self.update_quality_options()
        self._check_ffmpeg_status()

    def _apply_windows11_titlebar(self):
        """Sets Windows 11 title bar accent color (#E53E3E -> BGR 0x003E3EE5)."""
        try:
            hwnd = windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            # DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, byref(c_int(0x003E3EE5)), sizeof(c_int))
        except Exception:
            pass

    def _check_ffmpeg_status(self):
        if self.ffmpeg_path:
            self.status.configure(text="Ready • FFmpeg detected")
        else:
            self.status.configure(
                text="Ready • ⚠️ FFmpeg not detected (720p+ & MP3 conversion requires FFmpeg)",
                text_color="#F6AD55"
            )

    def _build_ui(self):
        # Header / Title
        self.header_label = ctk.CTkLabel(
            self, text="PyRed Downloader", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_label.pack(pady=(15, 5))

        # URL Input Section
        self.url_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.url_frame.pack(pady=(5, 5), padx=40, fill='x')

        self.url_label = ctk.CTkLabel(self.url_frame, text="YouTube URL:", anchor="w")
        self.url_label.pack(anchor="w", padx=5)

        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            border_color=RED_NORMAL,
            fg_color="#1A202C",
            placeholder_text_color="gray",
            height=36
        )
        self.url_entry.pack(pady=(2, 0), fill='x')

        # Destination Folder Frame
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(pady=6, padx=40, fill='x')

        self.folder_button = ctk.CTkButton(
            self.folder_frame,
            text="Choose Folder",
            width=130,
            command=self.choose_folder,
            fg_color=RED_NORMAL,
            hover_color=RED_HOVER
        )
        self.folder_button.pack(side="left")

        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text="Save to: Downloads",
            anchor="w",
            text_color="#CBD5E0"
        )
        self.folder_label.pack(side="left", padx=10, fill="x", expand=True)

        # Options Card Frame
        self.options_frame = ctk.CTkFrame(self, fg_color="#1A202C", corner_radius=8)
        self.options_frame.pack(pady=8, padx=40, fill="x")

        # Download Type Selector
        self.download_type_label = ctk.CTkLabel(
            self.options_frame, text="Format Type:", font=ctk.CTkFont(weight="bold")
        )
        self.download_type_label.pack(pady=(10, 2), padx=15, anchor="w")

        self.download_type_var = ctk.StringVar(value="Video + Audio")
        self.download_type_menu = ctk.CTkSegmentedButton(
            self.options_frame,
            values=["Video + Audio", "Video Only", "Audio Only"],
            variable=self.download_type_var,
            command=self.update_quality_options,
            selected_color=RED_NORMAL,
            selected_hover_color=RED_HOVER,
            unselected_hover_color=RED_DARK
        )
        self.download_type_menu.pack(pady=4, padx=15, fill="x")

        # Quality Selector
        self.quality_label = ctk.CTkLabel(
            self.options_frame, text="Quality / Bitrate:", font=ctk.CTkFont(weight="bold")
        )
        self.quality_label.pack(pady=(8, 2), padx=15, anchor="w")

        self.quality_var = ctk.StringVar()
        self.quality_menu = ctk.CTkOptionMenu(
            self.options_frame,
            variable=self.quality_var,
            values=[],
            fg_color=RED_NORMAL,
            button_color=RED_NORMAL,
            button_hover_color=RED_HOVER,
            dropdown_hover_color=RED_HOVER
        )
        self.quality_menu.pack(pady=(2, 12), padx=15, fill="x")

        # Video Clipping Frame
        self.clip_frame = ctk.CTkFrame(self, fg_color="#1A202C", corner_radius=8)
        self.clip_frame.pack(pady=8, padx=40, fill="x")

        self.use_clip_var = ctk.BooleanVar(value=False)
        self.clip_checkbox = ctk.CTkCheckBox(
            self.clip_frame,
            text="Enable Video Range Clipping",
            variable=self.use_clip_var,
            command=self.toggle_clip_inputs,
            fg_color=RED_NORMAL,
            hover_color=RED_HOVER,
            font=ctk.CTkFont(weight="bold")
        )
        self.clip_checkbox.pack(pady=(10, 5), padx=15, anchor="w")

        self.get_info_button = ctk.CTkButton(
            self.clip_frame,
            text="Fetch Video Duration (Enables Sliders)",
            command=self.fetch_video_info,
            state="disabled",
            fg_color="#333333",
            hover_color="#444444"
        )
        self.get_info_button.pack(pady=4, padx=15, fill="x")

        # Sliders Frame
        self.sliders_frame = ctk.CTkFrame(self.clip_frame, fg_color="transparent")

        self.start_slider_label = ctk.CTkLabel(self.sliders_frame, text="Start:", width=45, anchor="w")
        self.start_slider_label.grid(row=0, column=0, padx=5, sticky="w")
        self.start_slider = ctk.CTkSlider(
            self.sliders_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.on_start_slide,
            progress_color=RED_NORMAL,
            button_color=RED_NORMAL,
            button_hover_color=RED_HOVER
        )
        self.start_slider.set(0)
        self.start_slider.grid(row=0, column=1, padx=5, sticky="ew")

        self.end_slider_label = ctk.CTkLabel(self.sliders_frame, text="End:", width=45, anchor="w")
        self.end_slider_label.grid(row=1, column=0, padx=5, sticky="w")
        self.end_slider = ctk.CTkSlider(
            self.sliders_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.on_end_slide,
            progress_color=RED_NORMAL,
            button_color=RED_NORMAL,
            button_hover_color=RED_HOVER
        )
        self.end_slider.set(100)
        self.end_slider.grid(row=1, column=1, padx=5, sticky="ew")
        self.sliders_frame.columnconfigure(1, weight=1)

        # Time Inputs
        self.time_input_frame = ctk.CTkFrame(self.clip_frame, fg_color="transparent")
        self.time_input_frame.pack(pady=(4, 10))

        self.start_time_entry = ctk.CTkEntry(
            self.time_input_frame, width=90, placeholder_text="00:00:00", border_color=RED_NORMAL
        )
        self.start_time_entry.grid(row=0, column=0, padx=5)

        self.lbl_to = ctk.CTkLabel(self.time_input_frame, text="to")
        self.lbl_to.grid(row=0, column=1, padx=5)

        self.end_time_entry = ctk.CTkEntry(
            self.time_input_frame, width=90, placeholder_text="00:00:10", border_color=RED_NORMAL
        )
        self.end_time_entry.grid(row=0, column=2, padx=5)

        self.toggle_clip_inputs()

        # Download Action Button
        self.download_button = ctk.CTkButton(
            self,
            text="Download Now",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self.start_download,
            fg_color=RED_NORMAL,
            hover_color=RED_HOVER
        )
        self.download_button.pack(pady=(12, 6), padx=40, fill='x')

        # Determinate Progress Bar
        self.progress = ctk.CTkProgressBar(
            self, mode='determinate', progress_color=RED_NORMAL, fg_color="#2D3748"
        )
        self.progress.pack(fill='x', padx=40, pady=(6, 4))
        self.progress.set(0.0)

        # Status Label
        self.status = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(size=12), text_color="#E2E8F0"
        )
        self.status.pack(pady=(2, 10))

    def toggle_clip_inputs(self):
        """Enables/disables clip controls based on checkbox state."""
        if self.use_clip_var.get():
            self.start_time_entry.configure(state="normal")
            self.end_time_entry.configure(state="normal")
            self.get_info_button.configure(state="normal", fg_color="#4A5568", hover_color="#718096")
        else:
            self.start_time_entry.configure(state="disabled")
            self.end_time_entry.configure(state="disabled")
            self.get_info_button.configure(state="disabled", fg_color="#333333")
            self.sliders_frame.pack_forget()

    def fetch_video_info(self):
        """Fetches video duration for configuring slider boundaries."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Please enter a valid YouTube URL first.")
            return

        self.status.configure(text="Fetching video metadata...")
        self.get_info_button.configure(state="disabled", text="Loading video info...")

        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extract_flat': False
            }
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                title = info.get('title', 'Video')

            self.after(0, self.setup_sliders, duration, title)
        except Exception as e:
            err = str(e)
            self.after(0, lambda: messagebox.showerror("Metadata Error", f"Could not fetch video info:\n{err}"))
            self.after(0, lambda: self.status.configure(text="Error fetching metadata"))
        finally:
            self.after(0, lambda: self.get_info_button.configure(state="normal", text="Refresh Duration"))

    def setup_sliders(self, duration, title=""):
        self.video_duration = duration
        dur_str = self.format_seconds(duration)
        short_title = (title[:40] + '...') if len(title) > 40 else title
        self.status.configure(text=f"Loaded: {short_title} ({dur_str})")

        self.sliders_frame.pack(pady=5, padx=15, fill="x", after=self.get_info_button)
        self.start_slider.configure(to=duration, number_of_steps=max(duration, 1))
        self.end_slider.configure(to=duration, number_of_steps=max(duration, 1))
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
            if len(parts) == 1:
                return parts[0]
            if len(parts) == 2:
                return parts[0] * 60 + parts[1]
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            return None
        except ValueError:
            return None

    def update_quality_options(self, value=None):
        download_type = self.download_type_var.get()
        if "Video" in download_type:
            options = ["2160 (4K)", "1440 (2K)", "1080 (HD)", "720 (HD)", "best (Highest available)"]
            self.quality_menu.configure(values=options)
            self.quality_var.set("1080 (HD)")
        elif "Audio" in download_type:
            options = ["MP3 - 320k (Best)", "MP3 - 192k (High)", "MP3 - 128k (Medium)", "M4A - Best (Recommended)"]
            self.quality_menu.configure(values=options)
            self.quality_var.set("MP3 - 320k (Best)")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.folder_label.configure(text=f"Save to: {self.output_folder}")

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
                messagebox.showerror("Error", "Invalid time format. Please use HH:MM:SS or MM:SS.")
                return
            if start_sec >= end_sec:
                messagebox.showerror("Error", "End time must be greater than Start time.")
                return

        self.download_button.configure(state="disabled")
        self.progress.set(0.0)
        threading.Thread(target=self.download_video, args=(url, start_sec, end_sec), daemon=True).start()

    def download_video(self, url, start_sec, end_sec):
        self.after(0, lambda: self.status.configure(text="Initializing download..."))

        download_type = self.download_type_var.get()
        quality_str = self.quality_var.get()

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'windowsfilenames': True,
            'progress_hooks': [self.progress_hook],
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
        }

        # Connect FFmpeg
        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        # Clipping configuration
        if start_sec is not None and end_sec is not None:
            ydl_opts['download_ranges'] = download_range_func(None, [(start_sec, end_sec)])
            ydl_opts['force_keyframes_at_cuts'] = True

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

            elif "Audio" in download_type:
                ydl_opts['format'] = 'bestaudio/best'
                if "MP3" in quality_str:
                    codec = 'mp3'
                    audio_quality = '320' if "320k" in quality_str else '192' if "192k" in quality_str else '128'
                elif "M4A" in quality_str:
                    codec = 'm4a'
                    audio_quality = '192'
                else:
                    codec = 'mp3'
                    audio_quality = '192'

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
            err = str(e)
            if "ffmpeg" in err.lower() and not self.ffmpeg_path:
                err = "FFmpeg is required for this operation. Please install FFmpeg (e.g. winget install Gyan.FFmpeg) and restart."
            self.after(0, self.on_download_finished, False, err)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed')
            eta = d.get('eta')

            if total and total > 0:
                fraction = min(max(downloaded / total, 0.0), 1.0)
                pct = f"{fraction * 100:.1f}%"
                self.after(0, lambda f=fraction: self.progress.set(f))
            else:
                pct = d.get('_percent_str', '').strip() or "Downloading..."

            speed_text = f" • {speed / (1024 * 1024):.1f} MB/s" if speed else ""
            eta_text = f" • ETA {datetime.timedelta(seconds=int(eta))}" if eta else ""
            status_text = f"Downloading: {pct}{speed_text}{eta_text}"

            self.after(0, lambda t=status_text: self.status.configure(text=t))

        elif d['status'] == 'finished':
            self.after(0, lambda: self.progress.set(1.0))
            is_post = 'postprocessor' in d.get('info_dict', {}).get('filepath', '')
            msg = "Converting audio with FFmpeg..." if is_post else "Processing & merging files..."
            self.after(0, lambda m=msg: self.status.configure(text=m))

    def on_download_finished(self, success, error_message):
        self.download_button.configure(state="normal")
        if success:
            self.progress.set(1.0)
            self.status.configure(text="Download Complete! Saved in destination folder.")
            messagebox.showinfo("Success", f"Download complete!\n\nSaved to: {self.output_folder}")
        else:
            self.progress.set(0.0)
            self.status.configure(text="Download Failed")
            messagebox.showerror("Download Error", f"Download failed:\n{error_message}")


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
