import matplotlib.pyplot as plt
import mplcursors

values = [10, 20]
labels = ["User Time Taken", "Industrial Expected Time"]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values, color=['skyblue', 'orange'], edgecolor='black')
mplcursors.cursor(bars, hover=True)
plt.show()