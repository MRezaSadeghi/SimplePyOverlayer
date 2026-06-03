import json
import os
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import pandas as pd

from config import paths
from logrecorder.logger import logger


class Overlayer:
    def __init__(self):

        self.ass_file = paths.TEMP_ASS
        self.out_vid_file = paths.TEMP_VIDEO
        self.init_path = Path(__file__).parent

        self.required_cols = ["frame"]

        # vid file types
        self.vid_filetypes = [
            ("Video files", "*.mp4 *.mkv"),
            ("MP4 files", "*.mp4"),
            ("MKV files", "*.mkv"),
            ("All files", "*.*"),
        ]

        self.data_filetypes = [
            ("Data", "*.csv *.xlsx"),
            ("All files", "*.*"),
        ]

    def sec_to_ass_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60

        return f"{h}:{m:02d}:{s:05.2f}"

    def select_file(self, title="Select a File", filetypes=None) -> Path:

        root = tk.Tk()
        root.withdraw()

        if filetypes is None:
            filetypes = [("All files", "*.*")]

        initial_dir = self.init_path
        if initial_dir and isinstance(initial_dir, Path):
            initial_dir = str(initial_dir)

        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir,  # Start from folder X
        )

        root.destroy()
        return Path(file_path) if file_path else None

    def get_video_info(self, vid_path: Path) -> dict:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(vid_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        data = json.loads(result.stdout)

        video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")

        width = int(video_stream["width"])
        height = int(video_stream["height"])

        duration = float(data["format"]["duration"])

        fps_num, fps_den = map(int, video_stream["r_frame_rate"].split("/"))

        fps = fps_num / fps_den

        return {"width": width, "height": height, "fps": fps, "duration": duration}

    def get_data_info(self, data_path: Path):
        data = pd.read_csv(data_path)
        return {"data": data, "cols": data.columns}

    def ask_save_path(
        self, title="Save File As", filetypes=None, initial_dir=None, initial_file=""
    ):
        """Ask user for save path"""
        root = tk.Tk()
        root.withdraw()

        if filetypes is None:
            filetypes = [("All files", "*.*")]

        if initial_dir and isinstance(initial_dir, Path):
            initial_dir = str(initial_dir)

        save_path = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir,
            initialfile=initial_file,
        )

        root.destroy()
        return Path(save_path) if save_path else None

    def _get_style_from_json(self) -> str:
        config_path = paths.VISUAL_SETTINGS
        """Read style configuration from JSON file and return formatted style line"""

        # Default style values (fallback if JSON doesn't exist)
        default_style = {
            "Name": "Default",
            "Fontname": "Arial",
            "Fontsize": 10,
            "PrimaryColour": "&H00FFFFFF",
            "SecondaryColour": "&H00FFFFFF",
            "OutlineColour": "&H00000000",
            "BackColour": "&H64000000",
            "Bold": 0,
            "Italic": 0,
            "Underline": 0,
            "StrikeOut": 0,
            "ScaleX": 100,
            "ScaleY": 100,
            "Spacing": 0,
            "Angle": 0,
            "BorderStyle": 1,
            "Outline": 2,
            "Shadow": 0,
            "Alignment": 7,
            "MarginL": 10,
            "MarginR": 10,
            "MarginV": 10,
            "Encoding": 1,
        }

        # Try to load from JSON file
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Update defaults with JSON values
                    if "style" in config:
                        default_style.update(config["style"])
            except (json.JSONDecodeError, IOError) as e:
                print(
                    f"Warning: Could not read {config_path}: {e}. Using default style."
                )

        # Build the style line
        style_values = [
            str(default_style["Name"]),
            str(default_style["Fontname"]),
            str(default_style["Fontsize"]),
            str(default_style["PrimaryColour"]),
            str(default_style["SecondaryColour"]),
            str(default_style["OutlineColour"]),
            str(default_style["BackColour"]),
            str(default_style["Bold"]),
            str(default_style["Italic"]),
            str(default_style["Underline"]),
            str(default_style["StrikeOut"]),
            str(default_style["ScaleX"]),
            str(default_style["ScaleY"]),
            str(default_style["Spacing"]),
            str(default_style["Angle"]),
            str(default_style["BorderStyle"]),
            str(default_style["Outline"]),
            str(default_style["Shadow"]),
            str(default_style["Alignment"]),
            str(default_style["MarginL"]),
            str(default_style["MarginR"]),
            str(default_style["MarginV"]),
            str(default_style["Encoding"]),
        ]

        return f"Style: {','.join(style_values)}"

    def create_ass_header(self):
        lines = []
        lines.append("[Script Info]")
        lines.append("ScriptType: v4.00+")
        lines.append("\n")
        lines.append("[V4+ Styles]")
        lines.append(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
        )

        # Read style from JSON file
        style_line = self._get_style_from_json()
        lines.append(style_line)

        lines.append("\n")
        lines.append("[Events]")
        lines.append(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        )
        lines.append("\n")

        ass_init = "\n".join(lines)
        return ass_init

    def create_overlay_text(
        self, data: pd.DataFrame, posits: dict, ass_init: str, fps: int
    ):

        for c in self.required_cols:
            if c not in data.columns:
                raise ValueError(f"Missing required column: {c}")

        overlay_columns = [c for c in data.columns if c not in self.required_cols]
        print(overlay_columns)

        with open(self.ass_file, "w", encoding="utf-8") as f:
            # add init lines
            f.write(ass_init)

            for i in range(len(data) - 1):
                start = self.sec_to_ass_time((data.iloc[i]["frame"] - 1) / fps)
                end = self.sec_to_ass_time((data.iloc[i]["frame"]) / fps)

                for col in overlay_columns:
                    value = data.iloc[i][col]

                    x, y = posits[col]

                    text = f"{{\\pos({x},{y})}}{col.upper()}: {value}"

                    line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

                    f.write(line)
        logger.info("ass file created")

    def assign_positions_to_names(self, names):
        output_file = paths.LOCZ_SETTINGS

        positions = {}

        for i, name in enumerate(names):
            positions[name] = {"x": 30, "y": i * 30 + 30}

        # Save to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(positions, f, indent=2, ensure_ascii=False)

        print(f"Positions saved to {output_file}")
        return positions

    def load_positions_as_tuples(self):
        json_file = paths.LOCZ_SETTINGS

        with open(json_file, "r", encoding="utf-8") as f:
            positions_dict = json.load(f)

        # Convert {"name": {"x": 100, "y": 120}} to {"name": (100, 120)}
        result = {}
        for name, coords in positions_dict.items():
            result[name] = (coords["x"], coords["y"])

        return result

    def generate_video(self, vid_path):
        ass_path = self.ass_file.as_posix().replace(":", r"\:")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(vid_path),
            "-vf",
            f"ass='{ass_path}'",
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

    def run(self):
        print("Starting up SimpleOverlayer...")
        print(f"Want to tweak the overlay's look? Check out {paths.VISUAL_SETTINGS}")
        input("Press Enter once you're happy with the visual settings...")

        ass_init = self.create_ass_header()

        print("Alright, first up - pick your raw video file...")
        vid_path = self.select_file(
            title="Select the target video file to overlay",
            filetypes=self.vid_filetypes,
        )
        if not vid_path:
            logger.error("No video selected")
            return

        vid_info = self.get_video_info(vid_path)
        print(vid_info)

        print("Now grab the info CSV file...")
        data_path = self.select_file(
            title="Select the info CSV file",
            filetypes=self.data_filetypes,
        )
        if not data_path:
            logger.error("No data selected")
            return

        data_info = self.get_data_info(data_path)
        print(data_info["cols"])

        self.assign_positions_to_names(data_info["cols"][1:])
        logger.info(
            f"Default positions assigned. Feel free to change them in {paths.LOCZ_SETTINGS}"
        )
        input(
            f"Ready? Press Enter if these placeholder settings work for you...\n(just remember: x < {vid_info['width']} and y < {vid_info['height']})"
        )

        positions_dict = self.load_positions_as_tuples()
        self.create_overlay_text(
            data_info["data"], positions_dict, ass_init, fps=vid_info["fps"]
        )
        self.generate_video(vid_path)

        # save as
        destination = self.ask_save_path(
            title="Save Video As",
            filetypes=[("Video files", "*.mp4 *.mkv"), ("All files", "*.*")],
            initial_dir=Path.home() / "Videos",
            initial_file=self.out_vid_file,
        )

        if destination:
            # Copy the file (keeps original)
            shutil.copy2(self.out_vid_file, destination)
            print(f"Copied to: {destination}")
