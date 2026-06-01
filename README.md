# SimplePyOverlayer

SimplePyOverlayer is a Python tool that overlays CSV time-series data onto video files using FFmpeg and ASS subtitles.

It is designed for fast, lightweight visualization of engineering and telemetry data such as:
- Engine RPM
- Temperature signals
- Pressure sensors
- Any time-series CSV data

The pipeline is optimized for performance by avoiding frame-by-frame Python rendering and using FFmpeg’s native subtitle rendering.

---

## Features

- CSV-based dynamic video overlays
- Custom (x, y) text positioning in pixels
- Automatic video metadata extraction (FPS, resolution, duration)
- Fast rendering using FFmpeg (no OpenCV frame rendering)
- MP4/MKV input support
- Compressed output video (H.264)
- Simple interactive workflow

---

## Requirements

### System Dependencies

Install FFmpeg and FFprobe:

https://ffmpeg.org/download.html

Make sure they are accessible from terminal:

```bash
ffmpeg -version
ffprobe -version
