#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
import time

# Initialize motors
mg1 = MediumMotor(OUTPUT_A)
engine = LargeMotor(OUTPUT_B)
mg2 = LargeMotor(OUTPUT_C)

#calculate engine idle
mg2.stop(stop_action="coast")

# Store results
results = []


for enjohn in range(10, 101, 10):
    engine.on(speed=enjohn)
    
    aSpeed = 0
    i=-100
    counter=0
    while(i<0):
        mg1.on(speed=i)
        cSpeed = mg2.speed
        if cSpeed==0 and counter<5:
            i+=1
            time.sleep(0.1)
            counter+=1
            continue
        elif abs(cSpeed)>0.1:
            i+=1
            time.sleep(0.1)
            counter+=1
            continue
        else:
            print(cSpeed)
            aSpeed = mg1.speed
            break
    
    # store results
    results.append((aSpeed, engine.speed, 0))
    print(str(aSpeed) + " : " + str(engine.speed))

mg1.off()
engine.off()

print(results)




print("Done!")
