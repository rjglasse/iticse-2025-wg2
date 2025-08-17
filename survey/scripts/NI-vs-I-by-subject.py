import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Data
data = [
    ("Algorithms and Data Structures", 19, "NI"),
    ("AI and Machine Learning", 10, "NI"),
    ("Blockchain Technology", 1, "NI"),
    ("Software Engineering", 20, "NI"),
    ("Compilers", 3, "NI"),
    ("Computer Architecture", 1, "NI"),
    ("Computer Games", 2, "NI"),
    ("Computer Networks", 4, "NI"),
    ("Cryptography", 1, "NI"),
    ("Data Science", 4, "NI"),
    ("Programming Languages", 4, "NI"),
    ("Distributed Computing", 1, "NI"),
    ("Databases", 8, "NI"),
    ("Human-Computer Interaction", 8, "NI"),
    ("Mobile Computing", 5, "NI"),
    ("Object-Oriented Programming", 10, "NI"),
    ("Operating Systems", 8, "NI"),
    ("Robotics", 1, "NI"),
    ("Security", 5, "NI"),
    ("Systems Programming", 1, "NI"),
    ("Theory of Computation", 6, "NI"),
    ("Web Development", 5, "NI"),
    ("Algorithms and Data Structures", 12, "I"),
    ("AI and Machine Learning", 9, "I"),
    ("Software Engineering", 22, "I"),
    ("Compilers", 3, "I"),
    ("Computer Games", 3, "I"),
    ("Computer Networks", 1, "I"),
    ("Data Science", 4, "I"),
    ("Databases", 9, "I"),
    ("Distributed Systems", 1, "I"),
    ("Parallel Programming", 2, "I"),
    ("Human-Computer Interaction", 7, "I"),
    ("Mobile Computing", 5, "I"),
    ("Object-Oriented Programming", 16, "I"),
    ("Operating Systems", 2, "I"),
    ("Programming Languages", 2, "I"),
    ("Security", 2, "I"),
    ("Theory of Computation", 5, "I"),
    ("Web Development", 10, "I"),
]

# Create DataFrame
df = pd.DataFrame(data, columns=["Subject", "Count", "Category"])

# Combine Distributed Computing and Distributed Systems
df["Subject"] = df["Subject"].replace({
    "Distributed Computing": "Distributed Systems"
})

# Pivot to wide format
pivot_df = df.pivot_table(index="Subject", columns="Category", values="Count", fill_value=0)

# Sort by total count
pivot_df["Total"] = pivot_df.sum(axis=1)
pivot_df = pivot_df.sort_values("Total", ascending=True)

# Get two distinct colors from viridis palette
viridis_colors = [cm.viridis(0.2), cm.viridis(0.8)]

# Plot
fig, ax = plt.subplots(figsize=(6, 9))
pivot_df[["NI", "I"]].plot(
    kind="barh",
    stacked=True,
    ax=ax,
    color=viridis_colors,
    edgecolor="none",
    width=0.6
)
# Remove frame around the chart while keeping axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.set_xlabel("Count")
ax.set_ylabel("")
ax.legend(["Non-Integrating", "Integrating"], title="Category of Educator", frameon=False)
# ax.set_title("Counts of Subjects by IntegratiEducator")
ax.grid(False)  # Remove grid lines

# Add totals at the end of bars
for i, total in enumerate(pivot_df["Total"]):
    ax.text(total + 0.6, i, str(int(total)), va='center', ha='left', fontsize=9)

plt.tight_layout()

# Save to charts directory as high-resolution PNG
plt.savefig("../charts/ni-vs-i-by-subject.png", dpi=300, bbox_inches='tight')
plt.show()
