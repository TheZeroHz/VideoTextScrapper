# 🎙️ N.A.M.O.R. x BUBT HUB - Audio Transcription System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-black)
![Python](https://img.shields.io/badge/python-3.8+-black)
![Flask](https://img.shields.io/badge/flask-2.0+-black)
![License](https://img.shields.io/badge/license-MIT-black)

**Transform audio and video into text with mesmerizing real-time typing animations**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 📌 Overview

**N.A.M.O.R. x BUBT HUB** is an advanced audio transcription web application that converts YouTube videos, audio files, and video files into accurate text transcriptions. What makes it special? A beautiful **character-by-character typing animation** that keeps users engaged during the transcription process!

### ✨ Why This Project?

Traditional transcription tools show a boring loading spinner. We've revolutionized the experience with:
- 🎨 Real-time typing animation that appears as text is processed
- ⏱️ Timestamped segments for easy navigation
- 🎬 Support for both YouTube URLs and direct file uploads
- 📱 Beautiful, responsive UI with dark theme
- 🚀 Progressive web app feel with smooth animations

---

## 🎯 Features

### Core Functionality
- ✅ **Smart Caption Detection** - Checks YouTube captions first (5-10x faster!)
- ✅ **YouTube Video Transcription** - Paste any YouTube URL and get instant transcription
- ✅ **Automatic Fallback** - Uses speech-to-text if no captions available
- ✅ **File Upload Support** - Upload audio (MP3, WAV, etc.) or video (MP4, AVI, MKV, etc.)
- ✅ **Real-Time Typing Animation** - Text appears character-by-character with blinking cursor
- ✅ **Timestamped Segments** - YouTube videos include time markers for easy reference
- ✅ **Progress Tracking** - Visual progress bar with detailed status messages
- ✅ **Source Indicators** - Shows if transcription came from captions (📄 CC) or audio (🎤 STT)

### User Experience
- 🎨 **Modern Black & White Theme** - Professional, sleek design
- 📊 **Smart Progress Display** - Users watch text appear instead of waiting
- ⚡ **Fast Processing** - 30-second audio chunks for optimal speed
- 🎭 **Engaging Animations** - Shimmer effects, smooth transitions, pulsing timestamps
- 📱 **Fully Responsive** - Works perfectly on desktop, tablet, and mobile

### Export & Sharing
- 📋 **Copy to Clipboard** - One-click copy of entire transcription
- 💾 **Download as TXT** - Save transcriptions with preserved formatting
- 🔗 **GitHub Integration** - Easy access to source code and updates

---

## 🎬 Demo

### YouTube Transcription
```
1. Paste URL: https://www.youtube.com/watch?v=example
2. Click "Transcribe"
3. Watch real-time typing animation
4. Get timestamped results:
   ⏱️ 00:00 - "Welcome to our tutorial..."
   ⏱️ 00:30 - "First, let's understand..."
```

### File Upload
```
1. Drag & drop any audio/video file
2. System extracts audio (if video)
3. Text appears character by character
4. Copy or download results
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed on your system
- pip (Python package manager)

### Step 1: Clone Repository
```bash
git clone https://github.com/TheZeroHz/namor-transcription.git
cd namor-transcription
```

### Step 2: Install Dependencies
```bash
pip install flask flask-cors speechrecognition pydub yt-dlp
```

### Step 3: Install FFmpeg

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Open in Browser
```
http://localhost:8888
```

---

## 📁 Project Structure

```
namor-transcription/
│
├── app.py                 # Flask backend server
├── templates/
│   └── index.html        # Frontend UI
├── uploads/              # Temporary file storage (auto-created)
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── USER_MANUAL.md       # Detailed user guide
```

---

## 🔧 Usage

### Basic Workflow

#### Method 1: YouTube URL
```python
1. Open app in browser
2. Select "YouTube URL" tab
3. Paste video link
4. Click "Transcribe"
5. Wait for typing animation
6. Copy or download result
```

#### Method 2: File Upload
```python
1. Open app in browser
2. Select "Upload Audio/Video" tab
3. Drag & drop file or click to browse
4. System processes automatically
5. Read text as it types out
6. Export when complete
```

### Supported Formats

**Audio Files:**
- MP3, WAV, M4A, AAC, OGG, FLAC, WMA

**Video Files:**
- MP4, AVI, MKV, MOV, FLV, WMV, WebM, M4V, MPEG, 3GP

---

## 🎨 Technology Stack

### Backend
- **Flask** - Web framework
- **SpeechRecognition** - Google Speech API wrapper
- **yt-dlp** - YouTube video downloader
- **Pydub** - Audio processing
- **FFmpeg** - Media conversion

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **Vanilla JavaScript** - Interactive features
- **Server-Sent Events (SSE)** - Real-time progress updates

### Design Features
- **Typing Animation** - Character-by-character text reveal
- **Progress Tracking** - Visual feedback at every stage
- **Responsive Design** - Mobile-first approach
- **Dark Theme** - Professional black & white aesthetic

---

## 🧠 How It Works

### Architecture Flow

```
┌─────────────────┐
│  User Input     │
│  (URL or File)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  YouTube Caption Check  │ ⚡ NEW!
│  - Check for CC/subs    │
│  - Download if exists   │
│  - Parse VTT format     │
└────────┬────────────────┘
         │
         ├─── Captions Found? ──> FAST PATH (5-10 sec) ──┐
         │                                                 │
         └─── No Captions ───────────────────────────────┐│
                                                          ││
         ┌────────────────────────────────────────────────┘│
         │  Flask Backend (STT Path)                       │
         │  - Download/Process audio                       │
         │  - Split into chunks                            │
         │  - Send to Google API                           │
         └────────┬────────────────────────────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │  Real-Time Updates      │
         │  - Progress: 0-100%     │
         │  - Partial results      │
         │  - Status messages      │
         │  - Source badge         │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │  Frontend Display       │
         │  - Typing animation     │
         │  - Visual feedback      │
         │  - Export options       │
         │  - CC/STT badge        │
         └─────────────────────────┘
```

### Processing Pipeline

1. **Input Handling**
   - YouTube: First check for captions/subtitles ⚡ NEW!
     - If found: Download VTT, parse, display (FAST!)
     - If not found: Proceed to audio download
   - File: Accept upload and validate format

2. **Audio Processing** (Only if no captions)
   - Convert to WAV format
   - Split into 30-second chunks
   - Optimize for speech recognition

3. **Transcription**
   - **Caption Mode**: Parse timestamps and text from VTT
   - **STT Mode**: Send chunks to Google Speech API
   - Process responses in real-time
   - Combine results with timestamps

4. **User Experience**
   - Stream results via Server-Sent Events
   - Trigger typing animation
   - Update progress bar
   - Show source badge (📄 CC or 🎤 STT)
   - Show live indicators

---

## 📊 Performance

### Speed Benchmarks

| Input Type | Duration | With Captions ⚡ | Without Captions |
|------------|----------|------------------|------------------|
| YouTube (2 min) | 2:00 | **~10 sec** 🚀 | ~45 seconds |
| YouTube (5 min) | 5:00 | **~25 sec** 🚀 | ~2 minutes |
| YouTube (10 min) | 10:00 | **~50 sec** 🚀 | ~4 minutes |
| MP3 (1 MB) | ~1:30 | N/A | ~30 seconds |
| MP4 Video (10 MB) | ~5:00 | N/A | ~3 minutes |

**💡 Speed Boost:** Videos with captions are **5-10x faster!**

*Times vary based on internet speed and audio quality*

### Optimization Features
- ✅ **Smart caption detection** - Checks YouTube CC first (5-10x faster!)
- ✅ VTT subtitle parsing with HTML tag removal
- ✅ Duplicate caption filtering
- ✅ 30-second chunk processing for parallel efficiency
- ✅ Adaptive typing speed (speeds up for longer texts)
- ✅ Background noise reduction
- ✅ Automatic audio normalization

---

## 🎯 API Endpoints

### POST `/transcribeYoutube`
Transcribe YouTube video from URL.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response (Stream):**
```
data: {"progress": 10, "message": "Downloading..."}
data: {"progress": 50, "partial": {"time": "00:00", "text": "Hello"}}
data: {"progress": 100, "transcriptions": [...]}
```

### POST `/uploadAudio`
Transcribe uploaded audio/video file.

**Request:**
- Form data with file upload
- Accepts: audio/*, video/*

**Response (Stream):**
```
data: {"progress": 20, "message": "Processing..."}
data: {"progress": 60, "partial_text": "Example text"}
data: {"progress": 100, "transcription": "Full text"}
```

---

## 🔒 Security & Privacy

### Data Handling
- ✅ Files processed in temporary storage
- ✅ Automatic deletion after transcription
- ✅ No permanent data storage
- ✅ No user tracking or analytics

### Best Practices
- 🔐 HTTPS recommended for production
- 🔐 Input validation on all uploads
- 🔐 File size limits enforced
- 🔐 Temporary file cleanup

---

## 🐛 Troubleshooting

### Common Issues

**YouTube Download Fails**
```
Error: HTTP 403 Forbidden
Solution: Update yt-dlp → pip install --upgrade yt-dlp
```

**Audio Not Recognized**
```
Error: Could not understand audio
Solution: Ensure clear speech, minimal background noise
```

**FFmpeg Not Found**
```
Error: FFmpeg is not installed
Solution: Install FFmpeg and add to system PATH
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Areas for Improvement
- [ ] Multi-language support (currently English only)
- [ ] Speaker diarization (identify different speakers)
- [ ] Export to SRT/VTT subtitle formats with proper timing
- [ ] Whisper API integration for faster speech-to-text
- [ ] Real-time microphone transcription
- [ ] Video player integration with synchronized text
- [x] ~~YouTube caption detection~~ ✅ Implemented!

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Rakib Hasan**
- GitHub: [@TheZeroHz](https://github.com/TheZeroHz)
- Project: N.A.M.O.R. x BUBT HUB

---

## 🙏 Acknowledgments

- **BUBT HUB Community** - For inspiration and feedback
- **Google Speech Recognition** - For free transcription API
- **yt-dlp Contributors** - For amazing YouTube downloading tool
- **FFmpeg Team** - For powerful media processing
- **Open Source Community** - For making this possible

---

## 📚 Documentation

- [User Manual](USER_MANUAL.md) - Detailed usage guide
- [API Documentation](#-api-endpoints) - Endpoint reference
- [Troubleshooting](#-troubleshooting) - Common issues

---

## 🌟 Show Your Support

If you find this project helpful, please consider:
- ⭐ **Star this repository**
- 🐛 **Report bugs**
- 💡 **Suggest features**
- 🔀 **Submit pull requests**

---

## 📞 Contact

Have questions? Want to collaborate?
- Open an issue on GitHub
- Reach out via GitHub profile

---

<div align="center">

**Made with ❤️ by Rakib Hasan**

[⬆ Back to Top](#-namor-x-bubt-hub---audio-transcription-system)

</div>
