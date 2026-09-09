import socket
import tkinter as tk
from tkmacosx import Button
import time

# safe socket connection setup so app doesn't crash if connection fails
s = None
try:
    s = socket.socket()
    s.settimeout(1.5)
    s.connect(("169.254.27.226", 9999))
    print("connected")
except:
    print("yo")


def speed_calc(current, wanted_wheel_speed):
    global battery_percentage

    #clamping backwards component to model real ecvt
    if wanted_wheel_speed<0:
        wanted_wheel_speed = max(wanted_wheel_speed, -300)

    # calculate MG2 speed from the requested wheel speed.
    mg2 = wanted_wheel_speed / 3.0

    # turn the engine on only at the maximum requested wheel speed.
    target_engine = 900*wanted_wheel_speed/1700 if wanted_wheel_speed >= 900 else 0.0

    if battery_percentage<25:
        #gotta get them batterys up
        target_engine=min(300, target_engine+100)
        battery_percentage+=0.1
        
    #equation we got from data analysis, this is the one that calculates mg1 based on mg2 and engine speed
    mg1 = (mg2 + 0.44254819615742197 - 0.25062775461909614*target_engine)/-0.26052916725290637

    #limiting mg1 to 1400, since the motor can't go faster than that, and if it does we have to recalculate the engine speed to make sure it is within limits
    if abs(mg1) > 1400.0:
        clamped = 1400.0 if mg1 > 0 else -1400.0

        target_engine = (mg2 + 0.44254819615742197 + 0.26052916725290637 * clamped) / 0.25062775461909614
        target_engine = max(min(target_engine, 900.0), 0)

        mg1 = (mg2 + 0.44254819615742197 - 0.25062775461909614*target_engine)/-0.26052916725290637

    #little bug where if the engine is at 0 and mg2 is at 0, mg1 will be a small negative number, which is not possible since two motors always have to spin
    mg1 = 0.0 if target_engine == 0 and mg2 == 0 else mg1

    #simulate battery drain based off our motors
    battery_percentage = (battery_percentage-abs(mg2/4000.0)-abs(mg1/10000.0))
        
    #add some battery if low (for sake of simulation, the battery can never really "die")
    battery_percentage = max(battery_percentage -0.5, 0) if battery_percentage < 25 else battery_percentage

    #round to 3 decimal places so package is smaller and easier to send over wifi
    return round(mg1, 3), round(target_engine, 3), round(mg2, 3)


fcolor = "gray"
font = "TkDefaultFont" 
current_speed = 0 
battery_percentage = 100
current_mode = 1 # 0 is eco, 1 is normal, 2 is sport
speed_adder = 50.0 #initialize this for now at normal mode

drive_mode = 0 #0 is neutral, 1 is reverse, 2 is drive

#setting mode (eco, normal, sport) and changing the text color to reflect which one is on
def set_mode(mode):
    global current_mode, speed_adder
    if mode == 0:
        current_mode = 0
        speed_adder = 50.0
        eco_button.config(fg="green")
        normal_button.config(fg="gray")
        sport_button.config(fg="gray")
    elif mode == 1:
        current_mode = 1
        speed_adder = 100.0
        normal_button.config(fg="darkblue")
        eco_button.config(fg="gray")
        sport_button.config(fg="gray")
    elif mode == 2:
        current_mode = 2
        speed_adder = 150.0
        sport_button.config(fg="darkred")
        eco_button.config(fg="gray")
        normal_button.config(fg="gray")

target_speed = 0.0
def speeder(i):
    global current_speed, speed_adder, battery_percentage, target_speed
    if get_drive_mode() == 0:
        return #if in neutral, don't do anything
    i = not i if get_drive_mode() == 1 else i #if in reverse, invert the input
    target_speed = current_speed + speed_adder if i else current_speed - speed_adder
    if get_drive_mode() == 1:
        target_speed == min(0, target_speed)
    elif get_drive_mode() == 2:
        target_speed=max(0, target_speed)
    target_speed= target_speed if target_speed<=1700 else 1700

def update_speed():
    global target_speed, current_speed, battery_percentage
    mg1=0
    mg2=0
    target_engine=0
    #basically the the speeder function changes the target speed
    if abs(target_speed - current_speed) > 0.1: # only update if there's a big difference
        if target_speed<0 and current_speed>0:
            current_speed=0
            target_speed=0
        elif target_speed>0 and current_speed<0:
            current_speed=0
            target_speed=0
        else:
            mg1, target_engine, mg2 = speed_calc(current_speed, target_speed)
            current_speed = target_speed

    else:
        delta = (200/speed_adder*current_speed/1000) if current_speed<0 else (-200/speed_adder*current_speed/1000) #regen if in drive or reverse, also dependent on drive mode type
        mg1, target_engine, mg2 = speed_calc(current_speed, current_speed+delta)
        battery_percentage+=(5/speed_adder*current_speed/1000)
        battery_percentage = min(battery_percentage, 100)
        current_speed = current_speed+delta 
        target_speed=current_speed

    #send it off
    payload = f"{mg1},{target_engine},{mg2}\n"
    print("sent")
    
    battery_label.config(text=f"{round(battery_percentage, 1)}%")
    speed_label.config(text=f"{round(current_speed,1)}")
    if target_engine == 0:
        mpg = 99.9
    else:
        mpg = 50.0 - (49.9 * target_engine / 900.0)
    mpg_label.config(text=f"{max(mpg, 0.1):.1f}")
    
    # make sure the socket is still connected before sending
    if s:
        try:
            s.send(payload.encode())
        except Exception as e:
            print(f"gosh darn it it disconnected")
    #rahhh recursion
    root.after(100, update_speed)




def set_drive_mode(i):
    global drive_mode, current_speed
    if i == 0:
        current_speed = 0
    elif i == 1:
        if current_speed > 0:
            reverse_button.config(fg="red")
            time.sleep(0.1)
            reverse_button.config(fg="gray")
            return #can't go into reverse if the car is moving forward
    elif i == 2:
        if current_speed < 0:
            drive_button.config(fg="red")
            time.sleep(0.1)
            drive_button.config(fg="gray")
            return #can't go into drive if the car is moving backwards
    drive_mode = i
    if i == 0:
        neutral_button.config(fg="darkblue")
        reverse_button.config(fg="gray")
        drive_button.config(fg="gray")
    elif i == 1:
        reverse_button.config(fg="darkblue")
        neutral_button.config(fg="gray")
        drive_button.config(fg="gray")
    elif i == 2:
        drive_button.config(fg="darkblue")
        neutral_button.config(fg="gray")
        reverse_button.config(fg="gray")

def get_drive_mode():
    return drive_mode
            

root = tk.Tk()
root.title("ECVT Control Panel")
root.geometry("550x450")
root.configure(bg="white")

panel_frame = tk.Frame(root, bg="gray")

mode_frame = tk.Frame(panel_frame, bg="white")
mode_frame.pack(anchor="e", pady=(0, 10))

sport_button = tk.Button(mode_frame, text="Sport", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_mode(2), width=8)
sport_button.pack(side="right", padx=(0, 6))

normal_button = tk.Button(mode_frame, text="Norm", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_mode(1), width=8)
normal_button.pack(side="right", padx=(0,6))

eco_button = tk.Button(mode_frame, text="Eco", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_mode(0), width=8)
eco_button.pack(side="right", padx=(0, 6))

gear_frame = tk.Frame(panel_frame, bg="white")
gear_frame.pack()

reverse_button = tk.Button(gear_frame, text="R", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_drive_mode(1), width=6)
reverse_button.pack(side="left", padx=(0, 8))

neutral_button = tk.Button(gear_frame, text="N", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_drive_mode(0), width=6)
neutral_button.pack(side="left", padx=(0, 8))

drive_button = tk.Button(gear_frame, text="D", font=(font, 25,"bold"), bg=fcolor, command=lambda: set_drive_mode(2), width=6)
drive_button.pack(side="left")

status_frame = tk.Frame(panel_frame, bg="gray")
status_frame.pack(anchor="center", pady=10)

battery_label2 = tk.Label(status_frame, text=f"Battery:", font=(font, 25), bg="gray", fg="white")
battery_label2.pack()

battery_label = tk.Label(status_frame, text=f"{battery_percentage}%", font=(font, 25, "bold"),bg="gray", fg="white")
battery_label.pack()

speed_label2 = tk.Label(status_frame, text=f"Speed: ", font=(font, 25),bg="gray", fg="white")
speed_label2.pack(pady=(6, 0))

speed_label = tk.Label(status_frame, text=f"{current_speed}", font=(font, 25, "bold"),bg="gray", fg="white")
speed_label.pack(pady=(6, 0), anchor="center")
    
mpg_label2 = tk.Label(status_frame, text="MPG:", font=(font, 25), bg="gray", fg="white")
mpg_label2.pack(pady=(6, 0))
    
mpg_label = tk.Label(status_frame, text="99.9", font=(font, 25, "bold"), bg="gray", fg="white")
mpg_label.pack(pady=(6, 0), anchor="center")

speed_frame = tk.Frame(panel_frame, bg="white")
speed_frame.pack(anchor="center", pady=10)

speed_up_button = tk.Button(speed_frame, text="Gas", font=(font, 25,"bold"), bg=fcolor, command=lambda: speeder(1), width=12)
speed_up_button.pack(side="top")

slow_down_button = tk.Button(speed_frame, text="Brake", font=(font, 25,"bold"), bg=fcolor, command=lambda: speeder(0), width=12)
slow_down_button.pack(side="bottom")



# Initialize UI button highlight states to match starting modes (Neutral & Normal)
set_drive_mode(0)
set_mode(1)
update_speed()

panel_frame.pack()

root.mainloop()


# while True:
#     print("Battery %: " + str(battery_percentage))
#     inp = input("Enter wanted_wheel_speed, m to change modes.\n")
#     if inp == "m":
#         print("Current mode: " + modes[current_mode])
#         new_mode = input("Enter new mode (eco, normal, sport/rush):\n")[0]
#         if new_mode == "e":
#             current_mode = 0
#             time_factor = 50.0
#         elif new_mode == "n":
#             current_mode = 1
#             time_factor = 75.0
#         elif new_mode == "s":
#             current_mode = 2
#             time_factor = 100.0
#         else:
#             print("Invalid mode, keeping current mode.")
#             continue
#     else: # can't have a value error crash the system
#         try:
#             inp = float(inp)
#         except ValueError:
#             print("sir that isn't an m or a number, try again")
#             continue

#     print("accelerating...")
#     i=0
#     while i < int(abs(inp-current_speed)/time_factor +0.5): #this is a little hacky, but it works to make sure the speed doesn't change too fast, slows acceleration down to a more realistic level (i think)
#         new_speed = current_speed + (inp-current_speed)/time_factor
#         mg1, target_engine, mg2 = speed_calc(current_speed, new_speed, battery_percentage, abs(inp-current_speed)/time_factor) #time factor division helps simplify code while also allowing changes in acc
#         current_speed = new_speed 
#         #simulate battery drain based off our motors
#         battery_percentage = (battery_percentage-(mg2/400.0)-(mg1/1000.0))

#         #add some battery if low (for sake of simulation, the battery can never really "die")
#         battery_percentage = max(battery_percentage +0.5, 0) if battery_percentage < 25 else battery_percentage

#         payload = f"{mg1},{target_engine},{mg2}\n"
#         s.send(payload.encode())
#         print("*")
#         i += 1

#     current_speed = inp #setting for next loop, since the wanted speed is now the current speed (or should be)

#     print(f"accelerated to {current_speed}")
