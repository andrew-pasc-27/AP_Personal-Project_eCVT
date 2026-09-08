#!/usr/bin/env python3
import socket
import time
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent, SpeedDPS
from ev3dev2.display import Display
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_4
from ev3dev2.button import Button
from ev3dev2.power import PowerSupply

#connect to my laptop, use a blank IP address to listen for any incoming connections, 9999 is the "password"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9998))
server.listen(1)
print("listening")

#connection (which is a new server) and address sent after the connection is established, conn sends/receives data, addr is computer address 
conn, addr = server.accept()
conn.settimeout(1.5)
print("connected")

JOYSTICK_CENTER = 47 #value of reflected intensity at joystick middle
OFFSET = 2 #deadzone because joystick has play
MAX_DRIVE_SPEED = 1700.0 #theoretical max
MAX_REVERSE_SPEED = -400.0 #chosen minimum speed
MG1_LIMIT = 1450.0 #just listed spec
ENGINE_MAX = 1000.0 #another listed spec
MG2_POWER_LIMIT = 0.9 #how much the joystick has to move beyond the center for engine to turn on (mg2 reached limit) (but normalized)
ENGINE_SPEED = 900.0 #speed when the engine has to turn on
TIME_STEP = 0.1 #how much time between loops
SPEED_MULTIPLIER = 25
THROTTLE_CURVE = 2.0 #higher values make low throttle gentler and high throttle stronger
REGEN_COEFFICIENT = 80.0 #higher coefficient results in lower regen force
LOW_BATTERY_VOLTAGE = 6.5
BATTERY_CHECK_INTERVAL = 3.0
HYBRID_BATTERY_START = 100.0
HYBRID_BATTERY_ASSIST_LEVEL = 25.0
batt = PowerSupply()
btn = Button() #d-pad on the ev3
lcd = Display()
cs = ColorSensor(INPUT_4) #joystick sensor
motor_a = MediumMotor(OUTPUT_A) #mg1
motor_b = LargeMotor(OUTPUT_B) #engine
motor_c = LargeMotor(OUTPUT_C) #mg2 (wrote this way because its easier to understand which port)


def target_speed_from_joystick():
    value = cs.reflected_light_intensity #finds reflected light intensity (in my build it goes from 20-100)

    if value > JOYSTICK_CENTER + OFFSET: #if the joystick intensity is greater than the center+deadzone (basically accelerate)
        drive_fraction = min(1.0, (value + OFFSET - JOYSTICK_CENTER)/(53+OFFSET))
        print(drive_fraction)
        on = True if drive_fraction>MG2_POWER_LIMIT else False #should engine be on
        return max((drive_fraction ** THROTTLE_CURVE) * SPEED_MULTIPLIER, 1.0), on
    elif value < JOYSTICK_CENTER - OFFSET:
        reverse_fraction = min(1.0, (JOYSTICK_CENTER - value)/54)
        return -max((reverse_fraction ** THROTTLE_CURVE) * SPEED_MULTIPLIER * 5, 1.0), False #engine not on in reverse, backwards should be faster
    else:
        return 0.0, False #when joystick @ center

def calculate_motor_speeds(current_speed, speed_adder, engine_on_fast):
    global hybrid_battery
    #name's pretty obvious (thats good functional abstraction ive been told (rip speed_calc))
    wanted_wheel_speed = current_speed + speed_adder 

    mg2 = wanted_wheel_speed / 3.0 
    mg2 = 0 if wanted_wheel_speed < 0 and current_speed>0 else mg2 #not really necessary because of lets go but whatever
    mg2 = 0 if wanted_wheel_speed > 0 and current_speed<0 else mg2
    engine_on = True if abs(mg2 * 3.0) >= ENGINE_SPEED and speed_adder>0 else False #speed when engine has to turn on
    target_engine = 0.0 

    if engine_on_fast and wanted_wheel_speed>0:
        target_engine = min(ENGINE_MAX, (600+wanted_wheel_speed/4.25)) #if the lever is pressed all the way we're flooring it so the engine should be on fast

    elif engine_on and wanted_wheel_speed>0:
        target_engine = ENGINE_SPEED*((wanted_wheel_speed-800.0)/(MAX_DRIVE_SPEED-900.0)) #engine not supposed to be on
        target_engine = min(ENGINE_MAX, max(400, target_engine)) #clamp

    elif hybrid_battery < HYBRID_BATTERY_ASSIST_LEVEL: #if the amount in the battery is less than the amount needed to sustain fully electrical operation
        target_engine = min(400, target_engine + 100)
        hybrid_battery = min(HYBRID_BATTERY_START, hybrid_battery + 0.1)

    mg1 = (mg2 + 0.44254819615742197 - 0.25062775461909614 * target_engine) / 0.26052916725290637 #calc mg1
    if abs(mg1) > MG1_LIMIT: #if over, stop it
        mg1 = MG1_LIMIT if mg1 > 0 else -MG1_LIMIT
        target_engine = (mg2 + 0.44254819615742197 - 0.26052916725290637 * mg1) / 0.25062775461909614
        target_engine = max(min(target_engine, ENGINE_MAX), 0.0)

    if target_engine == 0.0 and mg2 == 0.0: #since theres a constant in the equation need to account when everythings 0
        mg1 = 0.0

    hybrid_battery -= abs(mg2 / 2000.0) + abs(mg1 / 5000.0)
    hybrid_battery = max(hybrid_battery, 0.0)

    return mg1, target_engine, mg2

def set_motor_speeds(mg1, engine, mg2): #just put it in a function ig
    motor_a.on(SpeedDPS(mg1))
    motor_b.on(SpeedDPS(engine))
    motor_c.on(SpeedDPS(mg2))

def update_display(message = None):
    global current_speed, current_gear, battery_low, hybrid_battery
    gear_names = ["D", "N", "R"]
    if message:
        lcd.text_pixels(message, x=58, y=2, font="helvB18", clear_screen=False)
    elif battery_low:
        lcd.text_pixels("LOW BATTERY", x=34, y=2,font="helvB12", clear_screen=True)
    else:
        lcd.draw.rectangle((0, 0, 178, 128), fill='white') #so the whole screen doesnt have to be replaced
        lcd.text_pixels(gear_names[current_gear][0] + ", "+str(round(hybrid_battery),1)+"\n" + str(round(current_speed / 15, 1)) + "MPH", x=60, y=24,font="helvB24", clear_screen=False)
    lcd.update()

def check_battery():
    global battery_low
    battery_low = True if batt.measured_volts < LOW_BATTERY_VOLTAGE else False
    return battery_low

def is_button_pressed(): #when a button on d-pad is pressed
    global current_gear
    if btn.right:
        set_motor_speeds(0,0,0) #emergency brake
        update_display("BRAKE")
        return 0
    if btn.up:
        current_gear = 0 #up button signals drive
    elif btn.enter:
        current_gear = 1 #middle is neutral
    elif btn.down:
        current_gear = 2 #down is reverse
    return 1

def regen(): #it was getting too long and i didn't like copy/pasting
    global current_speed, hybrid_battery
    current_speed = 0.0 if abs(current_speed)<5.0 else current_speed
    if current_speed:
        delta = (-current_speed/REGEN_COEFFICIENT) #regen is opposite of current_speed (need to slow down)
        mg1, target_engine, mg2 = calculate_motor_speeds(current_speed, delta, False)
        set_motor_speeds(mg1, target_engine, mg2)
        current_speed += delta
        hybrid_battery = min(HYBRID_BATTERY_START,
                 hybrid_battery + (5.0 / SPEED_MULTIPLIER * abs(current_speed) / 1000.0))
        send((""+str(mg1)+","+str(target_engine)+","+str(mg2)+"\n"))
    else: 
        send("0.0,0.0,0.0\n")

def lets_go(i): #lets go as in the thing is going to go; let's do this!
    global current_speed
    speed_adder, fast_engine = target_speed_from_joystick()
    speed_adder = -speed_adder if i==2 else speed_adder
    if abs(speed_adder)<0.1:
        regen() #if speed_adder is basically 0 then just regen
    
    else:
        requested_speed = current_speed+speed_adder #need to check whether the speed the code is trying to get is within bounds
        if i==0:
            requested_speed = max(0, min(MAX_DRIVE_SPEED, requested_speed)) #can't go below 0 in drive
        elif i==2:
            requested_speed = max(MAX_REVERSE_SPEED, min(0, requested_speed)) #can't go above 0 in reverse
        speed_adder = requested_speed - current_speed #once everything passes, then we can recalc speed_adder (seems redundant but it works)
        mg1, engine, mg2 = calculate_motor_speeds(current_speed, speed_adder, fast_engine)
        set_motor_speeds(mg1, engine, mg2)
        current_speed += speed_adder 
        send((""+str(mg1)+","+str(engine)+","+str(mg2)+"\n"))

def send(inp):
    if conn:
        try:
            conn.send(str(inp).encode())
        except:
            pass

try:
    current_speed = 0.0 #always start at 0
    current_gear = 1 #start in neutral
    battery_low = False
    hybrid_battery = HYBRID_BATTERY_START
    frame_count = 0
    next_loop = time.time()
    while True:
        next_loop += TIME_STEP
        if is_button_pressed():
            if current_gear == 1:
                regen()
            elif current_gear == 0:
                lets_go(0)
            elif current_gear == 2:
                lets_go(2)
        else:
            current_speed = 0.0

        if frame_count % 30 == 0:
            check_battery()

        if frame_count % 2 == 0:
            update_display()
        frame_count += 1
        time_remaining = next_loop - time.time()
        if time_remaining > 0:
            time.sleep(time_remaining)
        
except KeyboardInterrupt: #i can back out with my keyboard or with the button on the ev3 so the while loop can be backed out of
    print("done")
finally:
    motor_a.off()
    motor_b.off()
    motor_c.off()