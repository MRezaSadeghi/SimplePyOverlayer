import numpy as np
import pandas as pd

from config import paths


def generate_dataframe(n_frames, seed=None):
    """
    Generate a dataframe with:
        frame       : 1..n_frames
        rpm         : slow random values between 1300 and 1550
        temperature : slow random values between 80 and 95
        P1          : slow random values between 100 and 120
        P2          : slow random values between 110 and 150
    """

    rng = np.random.default_rng(seed)

    def slow_signal(n, low, high, step_fraction=0.02):
        center = (low + high) / 2
        step = (high - low) * step_fraction

        x = np.zeros(n)
        x[0] = center

        for i in range(1, n):
            x[i] = x[i - 1] + rng.normal(0, step)

        return np.clip(x, low, high)

    df = pd.DataFrame(
        {
            "frame": np.arange(1, n_frames + 1),
            "rpm": slow_signal(n_frames, 1300, 1550),
            "temperature": slow_signal(n_frames, 80, 95),
            "P1": slow_signal(n_frames, 100, 120),
            "P2": slow_signal(n_frames, 110, 150),
        }
    )

    df = df.round(1)
    df.to_csv(paths.SAMPLE_INFO, index=False)
    return df


if __name__ == "__main__":
    generate_dataframe(n_frames=500, seed=42)
