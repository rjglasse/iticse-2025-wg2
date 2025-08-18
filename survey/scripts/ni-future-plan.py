import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from textwrap import wrap

# ----- Original data -----
rows = [
    ("Allow students to use GenAI responsibly in assignments", 33, "Integration"),
    ("Ask students to evaluate GenAI outputs critically", 30, "Integration"),
    ("Integrate GenAI into course projects", 21, "Integration"),
    ("Use GenAI for brainstorming and ideation", 20, "Integration"),
    ("Demonstrate GenAI tools in lectures", 17, "Integration"),
    ("No plan to integrate GenAI in courses", 16, "Non-Integration"),
    ("Involve students in analyzing GenAI (e.g., ethics & bias)", 13, "Integration"),
    ("Use GenAI for clarifying requirements", 10, "Integration"),
    ("Other...", 9, "Integration")
]

# Build DataFrame
df = pd.DataFrame(rows, columns=["Option", "Count", "Category"])

# Split counts into two columns (Integration vs Non-Integration)
df["Integration"] = df.apply(lambda r: r["Count"] if r["Category"] == "Integration" else 0, axis=1)
df["Non-Integration"] = df.apply(lambda r: r["Count"] if r["Category"] == "Non-Integration" else 0, axis=1)
wide = df[["Option", "Integration", "Non-Integration"]].copy()
wide["Total"] = wide["Integration"] + wide["Non-Integration"]

# Wrap labels at width=30
wide["OptionWrapped"] = wide["Option"].apply(lambda t: "\n".join(wrap(t, width=29)))
wide = wide.set_index("OptionWrapped")

# Colors (Integration darker, Non-Integration lighter)
colors_swapped = [cm.viridis(0.8), cm.viridis(0.2)]

# Plot
fig, ax = plt.subplots(figsize=(6, 6))
wide[["Integration", "Non-Integration"]].plot(
    kind="barh",
    stacked=True,
    ax=ax,
    color=colors_swapped,
    edgecolor="none",
    width=0.4
)

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylabel("")
ax.legend(["Integration", "Non-Integration"], title="Category", frameon=False)
ax.grid(False)
ax.invert_yaxis()  # Keep first item at top

# Add totals at the end of bars
for i, total in enumerate(wide["Total"]):
    ax.text(total + 0.6, i, str(total), va='center', ha='left', fontsize=10)

plt.tight_layout()

# Save high-resolution PNG
plt.savefig("../charts/ni-future-plan.png", dpi=300, bbox_inches="tight")
plt.show()
