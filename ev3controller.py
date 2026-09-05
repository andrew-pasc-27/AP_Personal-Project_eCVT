#!/usr/bin/env python3
import time
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent, SpeedDPS
from ev3dev2.display import Display
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_4
from ev3dev2.button import Button
from ev3dev2.power import PowerSupply

#ev3 standalone code file, used recommendations to make code more readable, so i used constants and tried to use more obvious names

JOYSTICK_CENTER = 47 #value of reflected intensity at joystick middle
OFFSET = 2 #deadzone because joystick has play
MAX_DRIVE_SPEED = 1700.0 #basically theoretical max
MAX_REVERSE_SPEED = -400.0 #chosen min speed
MG1_LIMIT = 1450.0 #just listed spec
ENGINE_MAX = 1000.0 #another listed spec
MG2_POWER_LIMIT = 40.0 #how much the joystick has to move beyond the center for engine to turn on (mg2 reached limit)
ENGINE_SPEED = 900.0 #speed when the engine has to turn on (in my car its about 51~52 mph)
TIME_STEP = 0.1 #how much time between loops
SPEED_MULTIPLIER=1.7 #accceleration
REGEN_COEFFICIENT=3.0 #lower is less (wow am i right)

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
        drive_fraction = (value - JOYSTICK_CENTER)
        on = True if drive_fraction>MG2_POWER_LIMIT else False #should engine be on
        return max(drive_fraction*SPEED_MULTIPLIER, 1.0), on 
    elif value < JOYSTICK_CENTER - OFFSET:
        reverse_fraction = (JOYSTICK_CENTER - value)*2 #need to multiply by two because of joystick weirdness
        return -max(reverse_fraction*SPEED_MULTIPLIER, 1.0), False #engine not on in reverse
    else:
        return 0.0, False #when joystick @ center


def calculate_motor_speeds(current_speed, speed_adder, engine_on):
    #name's pretty obvious (thats good functional abstraction ive been told (rip speed_calc))
    wanted_wheel_speed = current_speed + speed_adder 

    mg2 = wanted_wheel_speed / 3.0 
    mg2 = 0 if wanted_wheel_speed < 0 and current_speed>0 else mg2 #not really necessary because of lets go but whatever
    mg2 = 0 if wanted_wheel_speed > 0 and current_speed<0 else mg2
    engine_on = True if abs(mg2 * 3.0) >= ENGINE_SPEED and speed_adder>0 else engine_on #speed when engine has to turn on
    target_engine = 0.0 

    if engine_on and wanted_wheel_speed>0:
        target_engine = ENGINE_SPEED*((wanted_wheel_speed-800.0)/(MAX_DRIVE_SPEED-900.0)) #engine not supposed to be on (until i add battery functions again)
        target_engine = min(ENGINE_MAX, max(300, target_engine)) #clamp

    mg1 = (mg2 + 0.44254819615742197 - 0.25062775461909614 * target_engine) / -0.26052916725290637 #calc mg1
    if abs(mg1) > MG1_LIMIT: #if over, stop it
        mg1 = MG1_LIMIT if mg1 > 0 else -MG1_LIMIT
        target_engine = (mg2 + 0.44254819615742197 + 0.26052916725290637 * mg1) / 0.25062775461909614
        target_engine = max(min(target_engine, ENGINE_SPEED), 0.0)

    if target_engine == 0.0 and mg2 == 0.0: #since theres a constant in the equation need to account when everythings 0
        mg1 = 0.0

    return mg1, target_engine, mg2


def set_motor_speeds(mg1, engine, mg2): #just put it in a function ig
    motor_a.on(SpeedDPS(mg1))
    motor_b.on(SpeedDPS(engine))
    motor_c.on(SpeedDPS(mg2))

def update_display(): # i want to display stuff since this is supposed to be a standalone code file
    global current_speed, current_gear
    gear_names = ["Drive", "Neutral", "Reverse"]
    gear_name = gear_names[current_gear]
    lcd.text_pixels("Batt: "+ str(round(batt.measured_volts, 1))+"\n"+gear_name +"\n"+str(round(current_speed,1)), x=48, y=24, font="luBS24") #placing stuff on screen, eg Batt: 5.0 Drive 55.0
    lcd.update()

def is_button_pressed(): #when a button on d-pad is pressed
    global current_gear
    if btn.up:
        current_gear = 0 #up button signals drive
    elif btn.enter:
        current_gear = 1 #middle is neutral
    elif btn.down:
        current_gear = 2 #down is reverse

def regen(): #it was getting too long and i didn't like copy/pasting
    global current_speed
    current_speed = 0.0 if abs(current_speed)<5.0 else current_speed
    if current_speed:
        delta = (-current_speed/REGEN_COEFFICIENT) #regen is opposite of current_speed (need to slow down)
        mg1, target_engine, mg2 = calculate_motor_speeds(current_speed, delta, False)
        set_motor_speeds(mg1, target_engine, mg2)
        current_speed += delta
    else: 
        pass

def lets_go(i): #lets go as in the thing is going to go; let's do this!
    global current_speed
    speed_adder, yes_engine = target_speed_from_joystick()
    speed_adder = -speed_adder if i==2 else speed_adder
    if not speed_adder:
        regen() #if speed_adder is 0 then just regen
    
    else:
        requested_speed = current_speed+speed_adder #need to check whether the speed the code is trying to get is within bounds
        if i==0:
            requested_speed = max(0, min(MAX_DRIVE_SPEED, requested_speed)) #can't go below 0 in drive
        elif i==2:
            requested_speed = max(MAX_REVERSE_SPEED, min(0, requested_speed)) #can't go above 0 in reverse
        speed_adder = requested_speed - current_speed #once everything passes, then we can recalc speed_adder (seems redundant but it works)
        mg1, engine, mg2 = calculate_motor_speeds(current_speed, speed_adder, yes_engine)
        set_motor_speeds(mg1, engine, mg2)
        current_speed += speed_adder 


current_speed = 0.0 #always start at 0
current_gear = 1 #start in neutral

try:
    while True: #isn't this such an elegant while loop
        is_button_pressed()
        if current_gear == 1: #neutral
            regen()

        elif current_gear == 0: #drive
            lets_go(0)
            
        elif current_gear == 2: #reverse
            lets_go(2)

        update_display()
            
        time.sleep(TIME_STEP)

except KeyboardInterrupt: #i can back out with my keyboard or with the button on the ev3 so the while loop can be backed out of
    print("done")
finally:
    motor_a.off()
    motor_b.off()
    motor_c.off()