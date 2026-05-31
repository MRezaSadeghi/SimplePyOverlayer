from overlayer import Overlayer

ov = Overlayer(
    data_file_name="sample",
    vid_file_name="sample_01",
    positions={
        "RPM": (10, 20),
        "TEMP": (10, 40),
        "P1": (10, 200),
        "P2": (10, 220),
    },
)

ov.create_overlay_text()
ov.generate_video()
