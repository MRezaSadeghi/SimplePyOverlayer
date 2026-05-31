import subprocess

import pandas as pd

from config import paths
from logrecorder.logger import logger


class Overlayer:
    def __init__(
        self,
        data_file_name: str,
        vid_file_name: str,
        positions: dict,
        target_file_name: str = "sample",
    ):
        self.text_folder = paths.RAW_TEXT_FOLDER
        self.video_folder = paths.RAW_VIDEO_FOLDER
        self.export_folder = paths.EXPORT_FOLDER
        self.ass_file = self.export_folder / f"{target_file_name}.ass"
        self.out_vid_file = self.export_folder / f"{target_file_name}.mp4"
        self.in_vid_file = self.video_folder / f"{vid_file_name}.mp4"
        self.data_file = self.text_folder / f"{data_file_name}.csv"

        self.required_cols = ["time"]

        self.posits = positions

    def create_ass_header(self):
        lines = []
        lines.append("[Script Info]")
        lines.append("ScriptType: v4.00+")
        lines.append("\n")
        lines.append("[V4+ Styles]")
        lines.append(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
        )
        lines.append(
            "Style: Default,Arial,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1"
        )
        lines.append("\n")
        lines.append("[Events]")
        lines.append(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        )
        lines.append("\n")

        ass_init = "\n".join(lines)
        return ass_init

    def sec_to_ass_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60

        return f"{h}:{m:02d}:{s:05.2f}"

    def create_overlay_text(self):
        data = pd.read_csv(self.data_file)

        for c in self.required_cols:
            if c not in data.columns:
                raise ValueError(f"Missing required column: {c}")

        overlay_columns = [c for c in data.columns if c != "time"]
        print(overlay_columns)

        with open(self.ass_file, "w", encoding="utf-8") as f:
            # add init lines
            ass_init = self.create_ass_header()
            f.write(ass_init)

            for i in range(len(data) - 1):
                start = self.sec_to_ass_time(data.iloc[i]["time"])
                end = self.sec_to_ass_time(data.iloc[i + 1]["time"])

                for col in overlay_columns:
                    value = data.iloc[i][col]

                    x, y = self.posits[col]

                    text = f"{{\\pos({x},{y})}}{col.upper()}: {value}"

                    line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

                    f.write(line)
        logger.info("ass file created")

    def generate_video(self):
        ass_path = (
            r"data/exports/sample.ass"  # self.ass_file.as_posix().replace(":", r"\:")
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.in_vid_file),
            "-vf",
            f"ass={ass_path}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "copy",
            str(self.out_vid_file),
        ]

        subprocess.run(cmd, check=True)

        logger.info(f"Finished: {self.out_vid_file}")
