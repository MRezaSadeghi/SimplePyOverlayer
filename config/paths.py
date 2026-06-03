from pathlib import Path

ROOT = Path(__file__).parent.parent

# DATA FOLDERS
RAW_TEXT_FOLDER = ROOT / "data" / "raw_text"
RAW_VIDEO_FOLDER = ROOT / "data" / "raw_video"
TEMP_FOLDER = ROOT / "data" / "temp"

# temp files
TEMP_VIDEO = TEMP_FOLDER / "temp_video.mp4"
TEMP_ASS = TEMP_FOLDER / "temp_data.ass"

# BM files
SAMPLE_INFO = RAW_TEXT_FOLDER / "auto_generate_sample.csv"

# logger files
LOGGER_CONFIG = ROOT / "logrecorder/logger.ini"
LOG_FILE = ROOT / "logrecorder/log_data/log.txt"

# setting files
VISUAL_SETTINGS = ROOT / "user_settings" / "format.json"
LOCZ_SETTINGS = ROOT / "user_settings" / "placeholder.json"
