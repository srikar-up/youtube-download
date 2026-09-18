# 🔴 PyRed — YouTube Downloader & Clipper

A desktop YouTube video/audio downloader with a dark, red-accented UI, built in Python with **CustomTkinter** and powered by **yt-dlp**.

> ⚠️ Educational project. Only download content you have the right to download, and respect YouTube's Terms of Service and applicable copyright law.

---

## Features

- **Video downloads** from 720p up to 4K (2160p), via yt-dlp
- **Audio-only extraction** to MP3 / M4A, including high-bitrate options
- **Video clipping** — grab video length, then pick a start/end range with sliders instead of downloading the whole video
- **Live progress bar** with downloads running on a background thread, so the UI never freezes
- **Custom dark/red theme**, with an accent color of `#E53E3E`, and a red title bar on Windows 11

---

## Requirements

| Requirement | Notes |
|---|---|
| Python 3.10+ | [python.org](https://www.python.org) |
| FFmpeg | Required for merging video+audio and for clipping — the app will not run without it |

Python packages: `customtkinter`, `yt-dlp` (installed below).

---

## Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/srikar-up/youtube-download.git
   cd youtube-download
   ```

2. **(Recommended) Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install customtkinter yt-dlp
   ```

4. **Set up FFmpeg** (critical — the app depends on this)
   - Download an FFmpeg "Essentials" build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
   - Extract the ZIP and open the `bin` folder
   - Copy `ffmpeg.exe`
   - Place it in the same folder as `hlo.py`:
     ```
     youtube-download/
     ├── ffmpeg.exe   <-- required
     ├── hlo.py       <-- main script
     └── README.md
     ```

---

## Usage

Run the app:

```bash
python hlo.py
```

Then:

1. **Paste** a YouTube URL
2. **Choose a format** — Video + Audio, Video Only, or Audio Only
3. **Pick a quality** — 720p / 1080p / 4K, or an audio bitrate
4. *(Optional)* **Clip the video**:
   - Enable clipping
   - Click "Get Video Length"
   - Drag the sliders to set a start and end point
5. **Download** and choose where to save the file

---

## Troubleshooting

| Problem | Fix |
|---|---|
| App crashes / FFmpeg error | Make sure `ffmpeg.exe` sits next to `hlo.py` |
| Title bar isn't red | Only supported on Windows 11 |
| Downloads are slow | Large 4K downloads can be throttled by YouTube — retry, or drop to a lower resolution |
| `ModuleNotFoundError` | Run `pip install customtkinter yt-dlp` again inside your active virtual environment |
| "Video unavailable" or extraction errors | yt-dlp needs regular updates to keep up with YouTube changes — run `pip install -U yt-dlp` |

---

## License

Released under the [MIT License](LICENSE). Provided for educational purposes only.
