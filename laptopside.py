import socket
from math import pi

s=socket.socket()
s.connect(("169.254.29.168", 9999))

def speed_calc(current, wanted_wheel_speed, battery_percentage, time_delta):
    time_delta = max(time_delta, 0.001) 
    # calculate mg2, target
    mg2 = wanted_wheel_speed/3.0
    current_mg2 = current/3.0

    mg2 = max(min(mg2, 300), -300)

    #acc and torque needed
    acc = (wanted_wheel_speed - current)/time_delta
    torque = 0.03 + (0.0002*acc)

    power = torque * abs(mg2) * pi/180

    max_battery_power = 2.5/100 * battery_percentage
    power_engine = max(0.0, power-max_battery_power)
    if battery_percentage < 20:
        target_engine = max(300, power_engine*120.0)
    else:
        target_engine = power_engine*120.0

    target_engine = max(min(target_engine, 900.0), 0)

    mg1 = (mg2 + 0.44254819615742197 + 0.25062775461909614*target_engine)/-0.26052916725290637

    if abs(mg1) > 1400.0:
        clamped = 1400.0 if mg1 > 0 else -1400.0

        target_engine = (mg2 + 0.44254819615742197 + 0.26052916725290637 * clamped) / -0.25062775461909614
        target_engine = max(min(target_engine, 900.0), 0)

        mg1 = (mg2 + 0.44254819615742197 + 0.25062775461909614*target_engine)/-0.26052916725290637
    if not mg2 and not target_engine:
        mg1 = 0.0
    return round(mg1, 3), round(target_engine, 3), round(mg2, 3)

new_john = 0

while True:
    input_str = input("Enter wanted_wheel_speed, battery_percentage, time_delta: ")
    inputs = list(map(float, input_str.split(',')))
    b,c,d = inputs
    mg1, target_engine, mg2 = speed_calc(new_john, b, c, d)
    new_john = b
    payload = f"{mg1},{target_engine},{mg2}\n"
    s.send(payload.encode())
    print(f"Calculated: mg1={mg1}, target_engine={target_engine}, mg2={mg2}")

