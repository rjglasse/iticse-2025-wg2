import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from textwrap import wrap

# ----- Original data -----
rows = [
("Prompt engineering", 26),
("None of the above", 25),
("Using GenAI to generate artefacts",17),
("Instruction on using GenAI to refine artefacts",15),
("Instruction on using GenAI to explain artefacts",14),
("Using GenAI to evaluate artefacts", 10),
("Using GenAI to decompose problems",	8),
("Other...",	1)
]

# Build DataFrame
df = pd.DataFrame(rows, columns=["Option", "Count"])

# Sort by count (descending)
df = df.sort_values("Count", ascending=True)

# Wrap labels at width=30
df["OptionWrapped"] = df["Option"].apply(lambda t: "\n".join(wrap(t, width=29)))
df = df.set_index("OptionWrapped")

# Create colors - dark for "None of the above", light for others
colors = []
for option in df["Option"]:
    if "None of the above" in option:
        colors.append(cm.viridis(0.2))  # Dark color for negative
    else:
        colors.append(cm.viridis(0.8))  # Light color for positive

# Plot
fig, ax = plt.subplots(figsize=(6, 5))
df["Count"].plot(
    kind="barh",
    ax=ax,
    color=colors,
    edgecolor="none",
    width=0.4
)

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel("")
ax.set_xlabel("Count")
ax.grid(False)

# Add totals at the end of bars
for i, total in enumerate(df["Count"]):
    ax.text(total + 0.8, i, str(int(total)), va='center', ha='left', fontsize=10)

plt.tight_layout()

# Save high-resolution PNG
plt.savefig("../charts/in-skills-to-teach.png", dpi=300, bbox_inches="tight")
plt.show()
