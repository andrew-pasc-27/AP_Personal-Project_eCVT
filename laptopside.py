import socket
from math import pi

#initialize socket connection
s=socket.socket()
#add ip address (changes every boot cycle), 9999 password
s.connect(("ev3dev ip address", 9999))

def speed_calc(current, wanted_wheel_speed, battery_percentage, time_delta):
    time_delta = max(time_delta, 0.001) 
    # calculate mg2, target
    mg2 = wanted_wheel_speed/3.0
    current_mg2 = current/3.0

    #large motor, but limited to model real world
    mg2 = max(min(mg2, 300), -300)

    #acc and torque needed
    acc = (wanted_wheel_speed - current)/time_delta
    torque = 0.03 + (0.0002*acc)

    #power needed
    power = torque * abs(mg2) * pi/180

    
    #calc max battery power, max power engine needs to output
    max_battery_power = 2.5/100 * battery_percentage
    power_engine = max(0.0, power-max_battery_power)

    #if battery too low, must have engine on to recharge
    if battery_percentage < 20:
        target_engine = max(300, power_engine*120.0)
    else:
        target_engine = power_engine*120.0

    #coding for max ang.velocity of large motor
    target_engine = max(min(target_engine, 900.0), 0)

    #equation got from data_analysis.py
    mg1 = (mg2 + 0.44254819615742197 + 0.25062775461909614*target_engine)/-0.26052916725290637
    
    #coding for max ang. velocity of a medium motor
    if abs(mg1) > 1400.0:
        clamped = 1400.0 if mg1 > 0 else -1400.0

        target_engine = (mg2 + 0.44254819615742197 + 0.26052916725290637 * clamped) / -0.25062775461909614

        #coding again for max ang. velocity
        target_engine = max(min(target_engine, 900.0), 0)

        mg1 = (mg2 + 0.44254819615742197 + 0.25062775461909614*target_engine)/-0.26052916725290637

    #if all values are 0, mg1 should be too (due to constants mg1 is >0 whch is bad
    if not mg2 and not target_engine:
        mg1 = 0.0

    #round each final value to 3 decimal places, shouldn't need any more
    return round(mg1, 3), round(target_engine, 3), round(mg2, 3)

#establish the current velocity of the car
current_velo = 0
while True:
    #ask for input
    input_str = input("Enter wanted_wheel_speed, battery_percentage, time_delta: ")
    inputs = list(map(float, input_str.split(',')))
    #map inputs to 3 values we can use in above function
    b,c,d = inputs
    #use current velo with 3 inputs
    mg1, target_engine, mg2 = speed_calc(current_velo, b, c, d)
    current_velo = b

    #send it off baby
    payload = f"{mg1},{target_engine},{mg2}\n"
    s.send(payload.encode())
    #making sure send was completed
    print(f"Calculated: mg1={mg1}, target_engine={target_engine}, mg2={mg2}")

