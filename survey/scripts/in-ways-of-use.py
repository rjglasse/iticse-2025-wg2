import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from textwrap import wrap

# ----- Original data -----
rows = [
    ("Allow students to use GenAI responsibly in assignments", 38),
    ("Ask students to evaluate GenAI outputs critically", 27),
    ("Use GenAI for brainstorming and ideation", 26),
    ("Integrate GenAI into course projects", 18),
    ("Demonstrate GenAI tools in lectures", 18),
    ("Use GenAI for clarifying requirements", 9),
    ("Involve students in analyzing GenAI (e.g., ethics & bias)", 9),
    ("Other", 6)
]

# Build DataFrame
df = pd.DataFrame(rows, columns=["Option", "Count"])

# Sort by count (descending)
df = df.sort_values("Count", ascending=True)

# Wrap labels at width=30
df["OptionWrapped"] = df["Option"].apply(lambda t: "\n".join(wrap(t, width=29)))
df = df.set_index("OptionWrapped")

# Single color for integrators
color = cm.viridis(0.8)

# Plot
fig, ax = plt.subplots(figsize=(6, 5))
df["Count"].plot(
    kind="barh",
    ax=ax,
    color=color,
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
plt.savefig("../charts/in-ways-of-use.png", dpi=300, bbox_inches="tight")
plt.show()
