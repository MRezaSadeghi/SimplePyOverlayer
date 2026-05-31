# color_formatter.py
import logging

RESET = "\033[0m"
COLORS = {
    logging.DEBUG:    "\033[35m",
    logging.INFO:     "\033[36m",
    logging.WARNING:  "\033[33m",
    logging.ERROR:    "\033[31m",
    logging.CRITICAL: "\033[41m",
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelno, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"