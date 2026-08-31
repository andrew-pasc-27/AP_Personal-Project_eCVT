#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
import time
#initialize motors
motor_a = MediumMotor(OUTPUT_A)
motor_b = LargeMotor(OUTPUT_B)
motor_c = LargeMotor(OUTPUT_C)

results = []
m = [motor_a, motor_b, motor_c]
#previously used another outer loop to loop through motors
#also allows for simple changing of motor depending on which test you want to run
for j in range(10, 101, 10):
    m[2].stop(stop_action="coast")
    m[0].on(speed=-j)
    m[1].on(speed=j)
    time.sleep(2)
    aSpeed = m[0].speed
    cSpeed = m[2].speed
    bSpeed = m[1].speed
    results.append((aSpeed, bSpeed, cSpeed))

motor_a.off()
motor_b.off()
motor_c.off()
#for copy and pasting into data_analysis.py
print(results)

print("Done!")
