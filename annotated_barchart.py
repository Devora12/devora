import matplotlib.pyplot as plt

# Data for the chart
values = [10, 20]
labels = ["User Time Taken", "Industrial Expected Time"]

# Create the bar chart
plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values, color=['skyblue', 'orange'], edgecolor='black')

# Annotate the bars with their values
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
        height + 0.5,  # Y-coordinate (slightly above the bar)
        f"{height:.2f} hours",  # Text to display
        ha='center',  # Horizontal alignment
        va='bottom',  # Vertical alignment
        fontsize=10,  # Font size
        color='black'  # Text color
    )

# Adjust the Y-axis limits to add extra space above the tallest bar
plt.ylim(0, max(values) + 5)  # Add 5 units of padding above the tallest bar

# Add labels and title
plt.ylabel("Time (hours)")
plt.title("Total Time: User vs Industrial Expected")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the chart
plt.show()