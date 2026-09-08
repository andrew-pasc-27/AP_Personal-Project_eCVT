import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import time

# safe socket connection setup so app doesn't crash if connection fails
s = None
try:
    s = socket.socket()
    s.connect(("169.254.109.183", 9998))
    print("connected")
except:
    print("yo")

MAX_LENGTH = 50
x_data = deque(maxlen=MAX_LENGTH) #found deques through google search
mg1_data = deque(maxlen=MAX_LENGTH)
engine_data = deque(maxlen=MAX_LENGTH)
mg2_data = deque(maxlen=MAX_LENGTH)
start_time = time.perf_counter()

fig, ax = plt.subplots(figsize=(8,4))
line1, = ax.plot([], [], lw = 2, color = "#06b6d4", label ="MG1")
line2, = ax.plot([], [], lw=2, color = "#14a020", label = "ENGINE")
line3, = ax.plot([], [], lw=2, color = "#d44e06", label = "MG2")

ax.set_title("Motor feed")
ax.set_xlabel("Time")
ax.set_ylabel("Motor Values")

plt.show(block=False)

def graph(x,y1,y2,y3):
    x_data.append(x)
    mg1_data.append(y1)
    engine_data.append(y2)
    mg2_data.append(y3)

    line1.set_data(x_data, mg1_data)
    line2.set_data(x_data, engine_data)
    line3.set_data(x_data, mg2_data)

    ax.relim()
    ax.autoscale_view(scalex=False, scaley=True)
    right = max(5.0, x_data[-1] + 0.1)
    ax.set_xlim(max(0.0, right - 5.0), right)
    

data_buffer = ""
while True:
    try:
        data_buffer += s.recv(1024).decode()
        lines = data_buffer.split("\n")
        data_buffer = lines.pop()
        for line in lines:
            if not line:
                continue
            mg1, engine, mg2 = map(float, line.split(","))
            graph((time.perf_counter() - start_time),mg1, engine, mg2)
            plt.pause(0.05)
    except KeyboardInterrupt:
        print("done")