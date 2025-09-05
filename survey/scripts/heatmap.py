# heatmap_white_purple_blue_landscape.py
# Requirements: matplotlib, pandas, numpy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap  # for older Matplotlib use LinearSegmentedColormap

# ---- Data ---------------------------------------------------------------
data = {
    "Subject": ["ADS", "SE", "HCI", "Web","TCS", "GAM"],
    "Generate": [58, 22, 57, 40, 40, 0],
    "Evaluate": [33, 33, 14, 20, 60, 20],
    "Interpret": [0, 11, 14, 0, 0, 0],
    "Refine": [0, 22, 0, 20, 0, 20],
    "Get Feedback": [0, 11, 0, 0, 0, 0],
    "Reflect": [8, 0, 0, 20, 0, 0],
    "Brainstorm": [0, 0, 0, 0, 0, 60],
    "Simulate": [0, 0, 14, 0, 0, 0],
    "Design": [0, 0, 0, 0, 0, 0]
}

df_heatmap = pd.DataFrame(data).set_index("Subject")

# Map abbreviations to full names
subject_map = {
    "ADS": "Algorithms & Data Structures",
    "SE":  "Software Engineering",
    "HCI": "Human–Computer Interaction",
    "Web": "Web Development",
    "TCS": "Theoretical Computer Science",
    "GAM": "Computer Games"
}

df_heatmap = df_heatmap.rename(index=subject_map)

# ---- Label wrapping helper ---------------------------------------------
def wrap_labels(labels, width=18):
    """Wrap long tick labels to multiple lines at the first space after ~width."""
    wrapped = []
    for lab in labels:
        if len(lab) <= width:
            wrapped.append(lab)
            continue
        # try to split near width on a space
        s = lab
        cut = s.rfind(" ", 0, width)
        if cut == -1:  # no space found before width, fall back to first space
            cut = s.find(" ")
        if cut == -1:  # no space at all
            wrapped.append(s)
        else:
            wrapped.append(s[:cut] + "\n" + s[cut+1:])
    return wrapped

# ---- Custom colormap: white -> purple -> blue (no green/yellow) --------
colors = [
    (1.0, 1.0, 1.0),   # white at 0
    (0.65, 0.50, 0.79),# soft purple
    (0.40, 0.33, 0.78),# deeper purple
    (0.23, 0.29, 0.75) # indigo/blue
]
cmap_wpb = LinearSegmentedColormap.from_list("white_purple_blue", colors, N=256)

# ---- Plot --------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 4))  # landscape for two-column float

im = ax.imshow(df_heatmap.values, cmap=cmap_wpb, aspect="auto", vmin=0, vmax=65)

# Ticks & wrapped labels
ax.set_xticks(np.arange(df_heatmap.shape[1]))
ax.set_yticks(np.arange(df_heatmap.shape[0]))
ax.set_xticklabels(df_heatmap.columns, rotation=45, ha="right")
ax.set_yticklabels(wrap_labels(df_heatmap.index.tolist(), width=18))

# Remove tick marks/gridlines; keep only tick labels
ax.tick_params(which="both", bottom=False, left=False, top=False, right=False)

# Annotate values in cells with legible color
for i in range(df_heatmap.shape[0]):
    for j in range(df_heatmap.shape[1]):
        val = df_heatmap.iat[i, j]
        text_color = "black" if val <= 20 else "white"
        ax.text(j, i, f"{val}", ha="center", va="center", color=text_color, fontsize=9)

# Colorbar
cbar = fig.colorbar(im, ax=ax, orientation="vertical")
cbar.set_label("Percentage")

# No title or axis labels
ax.set_title("")
ax.set_xlabel("")
ax.set_ylabel("")

fig.tight_layout()

# ---- Save --------------------------------------------------------------
fig.savefig("heatmap_instructors_activities.png", dpi=300, bbox_inches="tight")
fig.savefig("heatmap_instructors_activities.pdf", dpi=300, bbox_inches="tight")

print("Saved:",
      "heatmap_instructors_activities.png",
      "and",
      "heatmap_instructors_activities.pdf")
