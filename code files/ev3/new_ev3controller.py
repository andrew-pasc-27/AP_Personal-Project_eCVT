#!/usr/bin/env python3
import time
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedDPS
from ev3dev2.display import Display
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_4
from ev3dev2.button import Button
from ev3dev2.power import PowerSupply

#ev3 standalone code file, used recommendations to make code more readable, so i used constants and tried to use more obvious names

JOYSTICK_CENTER = 32 #value of reflected intensity at joystick middle
OFFSET = 1 #deadzone because joystick has play
MAX_DRIVE_SPEED = 1700.0 #theoretical max
MAX_REVERSE_SPEED = -400.0 #chosen minimum speed
MG1_LIMIT = 1450.0 #just listed spec
ENGINE_MAX = 1000.0 #another listed spec
TIME_STEP = 0.1 #how much time between loops
SPEED_MULTIPLIER = 40
THROTTLE_CURVE = 0.7 #higher values make low throttle gentler and high throttle stronger
CREEP_SPEED = 60.0 #low-speed target while the joystick is in its neutral deadzone
CREEP_STEP = 2.5 #maximum speed change per control loop while creeping
REGEN_COEFFICIENT = 75.0 #higher coefficient results in lower regen force
LOW_BATTERY_VOLTAGE = 6.0 #for ev3
BATTERY_CHECK_INTERVAL = 3.0
HYBRID_BATTERY_START = 100.0
HYBRID_BATTERY_ASSIST_LEVEL = 25.0
BRAKE_CURVE = 0.6
BRAKE_MULTIPLIER = 60

batt = PowerSupply()
btn = Button() #d-pad on the ev3
lcd = Display()
cs = ColorSensor(INPUT_4) #joystick sensor
motor_a = MediumMotor(OUTPUT_A) #mg1
motor_b = LargeMotor(OUTPUT_B) #engine
motor_c = LargeMotor(OUTPUT_C) #mg2 (wrote this way because its easier to understand which port)


def target_speed_from_joystick(value):
    #finds reflected light intensity (in my build it goes from 16-100, with a center of 32)

    if value > JOYSTICK_CENTER + OFFSET:
        drive_fraction = min(1.0,(value - JOYSTICK_CENTER - OFFSET)/(100 - JOYSTICK_CENTER - OFFSET))
        return (drive_fraction ** THROTTLE_CURVE) * SPEED_MULTIPLIER
    
    elif value < JOYSTICK_CENTER - OFFSET:
        reverse_fraction = min(1.0,(JOYSTICK_CENTER - OFFSET - value)/(JOYSTICK_CENTER - OFFSET - 16))
        
        return -((reverse_fraction ** BRAKE_CURVE) * BRAKE_MULTIPLIER) #braking needs more influence
    
    else:
        return 0.0 #when joystick @ center

class Engine:
    def __init__(self):
        self.max_rpm = ENGINE_MAX
        self.idle_rpm = 400.0
        self.rpm = 0.0
        self.mg2_power_limit = 0.9
        self.turn_on_speed = 900.0
        self.a, self.b, self.c, self.d, self.e = 0.001, 0.15, 200.0, 2.0, 0.05

    def engine_cost(self, rpm):
        return self.a * rpm ** 2 + self.b * rpm + self.c + self.d * (rpm > 0)

    def determine_rpm(self, current_speed, battery_level, acceleration):
        rpm = (self.a * current_speed ** 2 + self.b * current_speed + self.c
               + self.d * (100.0 - battery_level) + self.e * abs(acceleration))
        if rpm < self.idle_rpm:
            return self.idle_rpm
        return min(self.max_rpm, rpm)

    def battery_cost(self, mg2, current_speed):
        return self.e * abs(mg2) + abs(current_speed) / MAX_DRIVE_SPEED

    def should_run(self, rpm, mg2, drive_fraction, current_speed):
        forced_on = (drive_fraction > self.mg2_power_limit or
                     abs(current_speed) >= self.turn_on_speed)
        if rpm < self.idle_rpm:
            return forced_on
        return forced_on or self.battery_cost(mg2, current_speed) > self.engine_cost(rpm)

engine = Engine()

def calculate_motor_speeds(current_speed, speed_adder, joystick_value=None):
    global hybrid_battery
    wanted_wheel_speed = current_speed + speed_adder
    drive_fraction = min(1.0, (joystick_value + OFFSET - JOYSTICK_CENTER)/(68+OFFSET)) if joystick_value is not None else 0.0
    engine_on_fast = drive_fraction > engine.mg2_power_limit
    mg2 = wanted_wheel_speed / 3.0
    mg2 = 0 if wanted_wheel_speed < 0 and current_speed > 0 else mg2
    mg2 = 0 if wanted_wheel_speed > 0 and current_speed < 0 else mg2
    engine_on = abs(mg2 * 3.0) >= engine.turn_on_speed
    target_engine = 0.0

    if engine_on_fast and wanted_wheel_speed > 0:
        target_engine = min(engine.max_rpm, max(engine.idle_rpm, engine.rpm + 100 * current_speed / MAX_DRIVE_SPEED))
    elif engine_on and wanted_wheel_speed > 0:
        target_engine = engine.turn_on_speed * ((wanted_wheel_speed - 800.0) / (MAX_DRIVE_SPEED - engine.turn_on_speed))
        target_engine = min(engine.max_rpm, max(engine.idle_rpm, target_engine))
    elif hybrid_battery < HYBRID_BATTERY_ASSIST_LEVEL:
        target_engine = engine.idle_rpm
        hybrid_battery = min(HYBRID_BATTERY_START, hybrid_battery + 0.3)

    if engine.should_run(target_engine, mg2, drive_fraction, current_speed):
        target_engine = engine.determine_rpm(current_speed, hybrid_battery, speed_adder)

    mg1 = (mg2 + 0.44254819615742197 - 0.25062775461909614 * target_engine) / 0.26052916725290637
    if abs(mg1) > MG1_LIMIT:
        mg1 = MG1_LIMIT if mg1 > 0 else -MG1_LIMIT
        target_engine = (mg2 + 0.44254819615742197 - 0.26052916725290637 * mg1) / 0.25062775461909614
        target_engine = max(min(target_engine, engine.max_rpm), 0.0)

    if target_engine > 0.0 and abs(speed_adder) < 10 and mg2 != 0.0:
        hybrid_battery += abs(mg2 / 3000.0) - abs(mg1 / 5000.0)
    elif target_engine == 0.0 and mg2 == 0.0:
        mg1 = 0.0
    elif target_engine == 0.0 and speed_adder < 0:
        hybrid_battery += abs(mg2 / 3000.0) - abs(mg1 / 6000.0)
    elif target_engine > 0 and 10 < abs(speed_adder) < 16:
        hybrid_battery -= abs(mg1 / 6000.0)
    else:
        hybrid_battery -= abs(mg2 / 3000.0) + abs(mg1 / 5000.0)
    hybrid_battery = max(hybrid_battery, 0.0)
    engine.rpm = target_engine
    return mg1, target_engine, mg2

def set_motor_speeds(mg1, engine, mg2): #just put it in a function ig
    motor_a.on(SpeedDPS(mg1))
    motor_b.on(SpeedDPS(engine))
    motor_c.on(SpeedDPS(mg2))

def update_display(message = None):
    global current_speed, current_gear, battery_low, hybrid_battery
    gear_names = ["D", "N", "R"]
    if message:
        lcd.text_pixels(message, x=40, y=2, font="helvB18", clear_screen=False)
    elif battery_low:
        lcd.text_pixels("LOW BATTERY", x=34, y=2,font="helvB12", clear_screen=True)
    else:
        lcd.draw.rectangle((0, 0, 178, 128), fill='white') #so the whole screen doesnt have to be replaced
        lcd.text_pixels(gear_names[current_gear][0] + ", " + str(round(hybrid_battery, 1)) + "%\n" + str(round(current_speed / 15, 1)) + "MPH", x=60, y=24,font="helvB24", clear_screen=False)
    lcd.update()

def check_battery():
    global battery_low
    battery_low = True if batt.measured_volts< LOW_BATTERY_VOLTAGE else False
    return battery_low

def is_button_pressed(): #when a button on d-pad is pressed
    global current_gear
    brake_on = target_speed_from_joystick(cs.reflected_light_intensity) < -10.0 #checking if the brake is pressed down
    if btn.right or btn.left:
        set_motor_speeds(0,0,0) #emergency brake
        update_display("BRAKE")
        return 0
    if btn.up and brake_on:
        current_gear = 0 #up button signals drive
    elif btn.enter:
        current_gear = 1 #middle is neutral
    elif btn.down and brake_on:
        current_gear = 2 #down is reverse
    elif btn.up or btn.down:
        update_display("PRESS BRAKE")
        return 1
    return 1

def regen(): #it was getting too long and i didn't like copy/pasting
    global current_speed
    current_speed = 0.0 if abs(current_speed)<5.0 else current_speed
    if current_speed:
        delta = (-current_speed/REGEN_COEFFICIENT) #regen is opposite of current_speed (need to slow down)
        mg1, target_engine, mg2 = calculate_motor_speeds(current_speed, delta)
        set_motor_speeds(mg1, target_engine, mg2)
        current_speed += delta
    else: 
        pass

def lets_go(i): #lets go as in the thing is going to go; let's do this!
    global current_speed
    joystick_value = cs.reflected_light_intensity
    joystick_speed = target_speed_from_joystick(joystick_value)

    if joystick_speed < -40.0 and abs(current_speed) < CREEP_SPEED:
        # large brake input must suppress automatic creep in either gear.
        current_speed = 0.0
        mg1, engine_rpm, mg2 = calculate_motor_speeds(0.0, 0.0, joystick_value)
        set_motor_speeds(mg1, engine_rpm, mg2)
        return

    elif joystick_speed <= 0.0 and abs(current_speed) <= CREEP_SPEED:
        # move gradually toward a low crawl speed; use a negative target in reverse.
        creep_target = (CREEP_SPEED+joystick_speed) if i == 0 else -(CREEP_SPEED+joystick_speed)
        speed_adder = max(-CREEP_STEP, min(CREEP_STEP, creep_target - current_speed))
    
    elif abs(joystick_speed) < 0.1:
        regen() #if we are above creep speed, then regen to slow down to creep speed
        return
    
    else:
        speed_adder = -joystick_speed if i == 2 else joystick_speed

    requested_speed = current_speed + speed_adder
    if i == 0:
        requested_speed = max(0, min(MAX_DRIVE_SPEED, requested_speed)) #can't go below 0 in drive, also clamp to max speed
    elif i == 2:
        requested_speed = max(MAX_REVERSE_SPEED, min(0, requested_speed)) #can't go above 0 in reverse, also clamp to max reverse speed
    
    speed_adder = requested_speed - current_speed
    mg1, engine, mg2 = calculate_motor_speeds(current_speed, speed_adder, joystick_value)
    set_motor_speeds(mg1, engine, mg2)
    current_speed += speed_adder

current_speed = 0.0 #always start at 0
current_gear = 1 #start in neutral
battery_low = False
hybrid_battery = HYBRID_BATTERY_START
frame_count = 0
next_loop = time.time()

try:
    while True: #isn't this such an elegant while loop
        next_loop += TIME_STEP
        if is_button_pressed():
            if current_gear == 1: #neutral
                regen()

            elif current_gear == 0: #drive
                lets_go(0)
                
            elif current_gear == 2: #reverse
                lets_go(2)
        else:
            current_speed = 0.0

        if frame_count % 30 == 0:
            check_battery()

        if frame_count % 2 ==0:
            update_display()
        frame_count +=1
        time_remaining = next_loop - time.time()
        if (time_remaining)>0:
            time.sleep(time_remaining)


except KeyboardInterrupt: #i can back out with my keyboard or with the button on the ev3 so the while loop can be backed out of
    print("done")
finally:
    motor_a.off()
    motor_b.off()
    motor_c.off()
