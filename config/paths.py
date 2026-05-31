from pathlib import Path

ROOT = Path(__file__).parent.parent

# DATA FOLDERS
RAW_TEXT_FOLDER = ROOT / "data" / "raw_text"
RAW_VIDEO_FOLDER = ROOT / "data" / "raw_video"
EXPORT_FOLDER = ROOT / "data" / "exports"


# logger files
LOGGER_CONFIG = ROOT / "logrecorder/logger.ini"
LOG_FILE = ROOT / "logrecorder/log_data/log.txt"
