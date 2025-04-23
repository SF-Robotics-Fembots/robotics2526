import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create a figure and axis
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Initialize text
text = ax.text(5, 5, '', ha='center', va='center', fontsize=15)

# Update function for animation
def update(frame):
    text.set_text(f'{frame}')
    return text,

# Reset function to clear the text
def reset(event):
    text.set_text('')
    fig.canvas.draw()

# Create animation
ani = FuncAnimation(fig, update, frames=range(2016, 2025), interval=500, blit=True)

# Connect reset function to a button press event
fig.canvas.mpl_connect('button_press_event', reset)

plt.show()