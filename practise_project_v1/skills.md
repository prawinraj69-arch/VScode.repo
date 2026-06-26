# Skills — practise_project_v1

> Last updated: 2026-06-16

A living index of every script in this repo — what it does, what it uses, and how to run it.

---

## Projects

### 1. Hand-Gesture Anti-Gravity Painter
**File:** [V1_project/animation.py](V1_project/animation.py)

**What it does:**
- Tracks hand landmarks via webcam using MediaPipe Tasks `HandLandmarker`
- Pinch gesture (thumb + index finger) activates drawing mode
- Anti-gravity particles float upward while drawing
- Detects closed heart-shaped strokes via Hu Moments and auto-fills them with color

**Controls:** `q` quit | `c` clear canvas | `r` random color | `a` toggle particles

**Tech / Libraries:** `opencv-python`, `mediapipe`, `numpy`

**Run:**
```bash
python V1_project/animation.py
```

---

### 2. Daily Attendance Email Sender
**File:** [V1_project/attendence.py](V1_project/attendence.py)

**What it does:**
- Sends personalized attendance check-in emails with unique tokenized links
- Runs a lightweight HTTP server to track link clicks (check-ins)
- Logs check-ins to `attendance_log.csv`
- Sends the owner a notification email when someone marks attendance
- Supports a daily scheduler to send emails at a configured time

**Modes:**
| Flag | Action |
|------|--------|
| `--send-now` | Send today's emails immediately |
| `--serve` | Start the click-tracking HTTP server |
| `--schedule` | Run daily scheduler |
| `--run-all` | All of the above |
| `--status` | Show today's log entries |

**Tech / Libraries:** `smtplib`, `http.server`, `csv`, `threading`, `hashlib`

**Run:**
```bash
python V1_project/attendence.py --run-all
```

---

### 3. Real-Time Emotion Detection & AR Marker Demo
**File:** [V1_project/emotions.py](V1_project/emotions.py)

**What it does:**
- **Emotion mode:** Detects faces and predicts emotions (happy, sad, neutral, etc.) using FER (deep-learning model) or falls back to OpenCV Haar cascades
- Logs predictions to a CSV file at configurable intervals; `c` key saves snapshots
- **AR mode:** Detects ArUco markers (DICT_4X4_50) and overlays labels in real time

**Modes:**
```bash
python V1_project/emotions.py --mode emotion
python V1_project/emotions.py --mode ar
```

**Tech / Libraries:** `opencv-python`, `opencv-contrib-python`, `fer`, `numpy`

---

### 4. Daily Job Alert Email — The Muse API
**File:** [V1_project/job_application.py](V1_project/job_application.py)

**What it does:**
- Scrapes software engineering job listings from The Muse public jobs API
- Filters by location (Chennai), role keywords, and configurable trigger keywords (e.g., `etl`, `sql`, `jira`)
- Sends a formatted HTML email with up to 10 job cards daily
- Caches results to `jobs_cache.json` and falls back to it on network failure
- Runs on a daily schedule at a configured time (default `09:01`)

**Tech / Libraries:** `requests`, `schedule`, `smtplib`, `json`

**Run:**
```bash
python V1_project/job_application.py
```

---

### 5. Snake Game
**File:** [V1_project/snake_game.py](V1_project/snake_game.py)

**What it does:**
- Classic snake game on an 800×600 grid
- Primary renderer: **pygame** (smooth graphics, colored head)
- Fallback renderer: **tkinter** (runs without pygame installed)
- Arrow keys to move; `Space` to restart after game over

**Tech / Libraries:** `pygame` (primary), `tkinter` (fallback), `random`, `enum`

**Run:**
```bash
python V1_project/snake_game.py
```

---

### 6. Indian Stock Market Analyzer
**File:** [V1_project/share_market.py](V1_project/share_market.py)

**What it does:**
- Fetches 1-month daily OHLCV data for 50 NIFTY stocks via `yfinance`
- Scores each stock on 5 factors: 5-day momentum, monthly trend, volume ratio, daily change, price range position
- Prints ranked top-5 buy recommendations with metrics

**Tech / Libraries:** `yfinance`, `pandas`

**Run:**
```bash
python V1_project/share_market.py
```

---

### 7. WhatsApp Group Message Sender
**File:** [V1_project/watsapp_mess.py](V1_project/watsapp_mess.py)

**What it does:**
- Sends a message to a WhatsApp group via WhatsApp Web automation
- Accepts a raw group code or a full invite URL; schedules the send for 1 minute from now
- Requires you to be logged in to WhatsApp Web in the default browser

**Tech / Libraries:** `pywhatkit`

**Run:**
```bash
python V1_project/watsapp_mess.py
```

---

### 8. YouTube Audio Downloader
**File:** [V1_project/youtube_Download.py](V1_project/youtube_Download.py)

**What it does:**
- Downloads audio from a YouTube video or playlist and converts it to MP3 at 192 kbps
- Auto-installs `yt-dlp` if missing; requires `ffmpeg` on PATH for conversion
- Saves files to the same directory as the script

**Tech / Libraries:** `yt-dlp`, `ffmpeg` (system dependency)

**Run:**
```bash
python V1_project/youtube_Download.py "https://youtu.be/VIDEO_ID"
python V1_project/youtube_Download.py "https://youtube.com/playlist?list=..."
```

---

## Tech Stack Summary

| Category | Libraries / Tools |
|----------|-------------------|
| Computer Vision | `opencv-python`, `opencv-contrib-python`, `mediapipe` |
| Machine Learning | `fer` (emotion detection) |
| Data / Finance | `yfinance`, `pandas` |
| Game Dev | `pygame`, `tkinter` |
| Automation | `pywhatkit`, `yt-dlp`, `schedule` |
| Networking / Email | `smtplib`, `requests`, `http.server` |
| System | `ffmpeg` (external), `subprocess` |

---

## Environment Setup

```bash
# Create virtual environment and sync deps
uv venv
uv pip install pygame

# Per-project installs (run as needed)
uv pip install opencv-python mediapipe numpy
uv pip install fer opencv-contrib-python
uv pip install yfinance pandas
uv pip install pywhatkit
uv pip install yt-dlp requests schedule
```

> Python 3.10 or 3.11 recommended for pygame compatibility (see `requirements.txt`).
> Install uv: `pip install uv` or `winget install astral-sh.uv`
