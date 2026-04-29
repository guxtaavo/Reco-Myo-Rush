import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv("db/voluntary_010_center.csv")

channels = ["CH_1","CH_2","CH_3","CH_4","CH_5","CH_6","CH_7","CH_8"]

# Colors for each gesture
colors = {
    "POWER": "red",
    "LATERAL": "blue",
    "POINTER": "orange",
    "OPEN": "green",
    "TRIPOD": "purple",
    "REST": "gray"
}

# Create figure layout
fig, axes = plt.subplots(
    nrows=8, ncols=1,
    figsize=(14, 18),
    sharex=True
)

for i, ch in enumerate(channels):
    ax = axes[i]

    # Plot each gesture segment separately
    for state, color in colors.items():
        subset = df[df["State"] == state]
        ax.plot(subset["Timestamp"], subset[ch], color=color, linewidth=0.8, label=state)

    ax.set_ylabel(ch)

# Title
axes[0].set_title("EMG Channels — colorido por gesto")

# X label
axes[-1].set_xlabel("Timestamp")

# Add legend only once, outside the plots
fig.legend(colors.keys(), loc="upper right")

plt.tight_layout()
plt.show()
