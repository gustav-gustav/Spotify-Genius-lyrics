import json
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count

path = os.path.join(os.environ['LYRICS_PATH'], 'json', 'statistics.json')
index = count()
x = []
x_vals = []
y_vals = []

def animate(i):
    x.append(next(index))

    with open(path, 'r') as json_load:
        json_read = json.load(json_load)
        json_keys = json_read.keys()

        plt.cla()
        for key in json_keys:

            plt.plot([index for index in range(len(json_read[key]))],
                     json_read[key], label=key)

    plt.legend(loc='upper left')
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
