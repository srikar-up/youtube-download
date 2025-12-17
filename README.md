# 🎥 YouTube Downloader (Python & CustomTkinter)

A modern, dark-themed desktop application to download YouTube videos and audio. Built with Python, `CustomTkinter`, and `yt-dlp`, it features a clean **Red & Dark UI**, support for 4K downloads, and a built-in **Video Clipper**.

![App Screenshot](screenshots/main_ui.png)
*(Note: Add a screenshot of your app in a 'screenshots' folder)*

## ✨ Features

* **Modern GUI**: Built with `CustomTkinter` featuring a custom Red/Dark theme.
* **Video Clipping**: Download specific sections of a video (e.g., from 00:30 to 01:15) using interactive sliders.
* **High Quality**: Supports downloads up to **4K (2160p)** and **2K (1440p)**.
* **Audio Extraction**: Convert videos to high-quality **MP3** or **M4A**.
* **Smart Integration**:
    * Automatically changes the Windows 11 Title Bar color to match the app theme.
    * Multi-threaded downloads (UI doesn't freeze).
* **FFmpeg Power**: Uses FFmpeg for high-speed merging and precise cutting.

## 🛠️ Prerequisites

Before running the app, ensure you have the following installed:

1.  **Python 3.8+**: [Download Here](https://www.python.org/downloads/)
2.  **FFmpeg**: Required for merging video/audio and for the clipping function.

## 📦 Installation

