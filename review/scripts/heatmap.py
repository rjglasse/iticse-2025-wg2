# heatmap_white_purple_blue_landscape.py
# Requirements: matplotlib, pandas, numpy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap  # for older Matplotlib use LinearSegmentedColormap

# ---- Data ---------------------------------------------------------------
data = {
    "Subject": ["SE", "DB", "HCI", "ADS", "DSV", "OOP", "SEC", "ML", "NET", "TCS"],
    "Generate": [38, 44, 39, 14, 32, 33, 0, 22, 17, 50],
    "Evaluate": [13, 4, 9, 7, 14, 33, 73, 44, 17, 25],
    "Interpret": [12, 20, 4, 36, 18, 17, 27, 11, 67, 25],
    "Refine": [13, 4, 4, 21, 5, 0, 0, 22, 0, 0],
    "Get Feedback": [8, 4, 13, 21, 0, 17, 0, 0, 0, 0],
    "Reflect": [6, 16, 4, 0, 18, 0, 0, 0, 0, 0],
    "Brainstorm": [2, 0, 9, 0, 14, 0, 0, 0, 0, 0],
    "Simulate": [6, 4, 13, 0, 0, 0, 0, 0, 0, 0],
    "Design": [2, 4, 4, 0, 0, 0, 0, 0, 0, 0]
}
df_heatmap = pd.DataFrame(data).set_index("Subject")

# Map abbreviations to full names
subject_map = {
    "SE":  "Software Engineering",
    "DB":  "Databases",
    "HCI": "Human–Computer Interaction",
    "ADS": "Algorithms & Data Structures",
    "DSV": "Data Science & Visualization",
    "OOP": "Object-oriented Programming",
    "SEC": "Security",
    "ML": "Machine Learning",
    "NET": "Networks",
    "TCS": "Theoretical Computer Science"
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
fig, ax = plt.subplots(figsize=(14, 5))  # landscape for two-column float

im = ax.imshow(df_heatmap.values, cmap=cmap_wpb, aspect="auto", vmin=0, vmax=75)

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
fig.savefig("heatmap_white_purple_blue_landscape_fullnames_wrapped.png", dpi=300, bbox_inches="tight")
fig.savefig("heatmap_white_purple_blue_landscape_fullnames_wrapped.pdf", dpi=300, bbox_inches="tight")

print("Saved:",
      "heatmap_white_purple_blue_landscape_fullnames_wrapped.png",
      "and",
      "heatmap_white_purple_blue_landscape_fullnames_wrapped.pdf")
