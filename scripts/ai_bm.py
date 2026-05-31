import subprocess
from pathlib import Path

import pandas as pd

# ==========================================================
# USER SETTINGS
# ==========================================================

VIDEO_FILE = "input.mp4"
CSV_FILE = "data.csv"
OUTPUT_VIDEO = "output.mp4"

FONT_SIZE = 28

# pixel locations
POSITIONS = {
    "speed": (50, 50),
    "rpm": (50, 100),
    "temp": (50, 150),
}

# ==========================================================


def sec_to_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60

    return f"{h}:{m:02d}:{s:05.2f}"


df = pd.read_csv(CSV_FILE)

required_cols = ["time"]

for c in required_cols:
    if c not in df.columns:
        raise ValueError(f"Missing required column: {c}")

overlay_columns = [c for c in df.columns if c != "time"]

ass_file = Path("overlay.ass")

with open(ass_file, "w", encoding="utf-8") as f:
    # ASS Header
    f.write(
        """[Script Info]
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

Style: Default,Arial,28,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    )

    for i in range(len(df) - 1):
        start = sec_to_ass_time(df.iloc[i]["time"])
        end = sec_to_ass_time(df.iloc[i + 1]["time"])

        for col in overlay_columns:
            value = df.iloc[i][col]

            x, y = POSITIONS[col]

            text = f"{{\\pos({x},{y})}}{col.upper()}: {value}"

            line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

            f.write(line)

    # last row stays visible for 1 second
    last = df.iloc[-1]

    start = sec_to_ass_time(last["time"])
    end = sec_to_ass_time(last["time"] + 1)

    for col in overlay_columns:
        value = last[col]
        x, y = POSITIONS[col]

        text = f"{{\\pos({x},{y})}}{col.upper()}: {value}"

        line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

        f.write(line)

print("ASS subtitle created.")

cmd = [
    "ffmpeg",
    "-y",
    "-i",
    VIDEO_FILE,
    "-vf",
    f"ass={ass_file}",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-crf",
    "23",
    "-c:a",
    "copy",
    OUTPUT_VIDEO,
]

subprocess.run(cmd, check=True)

print(f"Finished: {OUTPUT_VIDEO}")
