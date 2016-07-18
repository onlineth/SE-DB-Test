from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt


fig, ax = plt.subplots()
ax = fig.add_subplot(111, projection='3d')

x1 = 1
x2 = 2
y1 = 1
y2 = 1
z1 = 2
z2 = 2

ax.plot([x1, x2], [y1, y2], [z1, z2], linewidth=2, picker=5)


def on_pick(event):
    event.artist.set_visible(not event.artist.get_visible())
    fig.canvas.draw()

fig.canvas.callbacks.connect('pick_event', on_pick)
plt.show()
