import pandas as pd
import matplotlib.pyplot as plt

# ======= SELECT YOUR CSV FILE HERE ========
csv_file = "db/right_full_gestures_random_00.csv"
# ==========================================

# Load the file
df = pd.read_csv(csv_file)

# Channels
channels = ["CH_1","CH_2","CH_3","CH_4","CH_5","CH_6","CH_7","CH_8"]

# Create figure
fig, axes = plt.subplots(
    nrows=8, ncols=1,
    figsize=(14, 18),
    sharex=True
)

for i, ch in enumerate(channels):
    ax = axes[i]
    ax.plot(df["Timestamp"], df[ch], linewidth=0.8)

    # Label channel
    ax.set_ylabel(ch)

# Title only on top plot
axes[0].set_title(f"EMG Channels — {csv_file}")

# X-axis label only on last plot
axes[-1].set_xlabel("Timestamp")

plt.tight_layout()
plt.show()
