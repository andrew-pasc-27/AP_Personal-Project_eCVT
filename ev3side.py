#!/usr/bin/env python3
import socket
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent, SpeedDPS

# initialize motors
motor_a = MediumMotor(OUTPUT_A)
motor_b = LargeMotor(OUTPUT_B)
motor_c = LargeMotor(OUTPUT_C)

#connect to my laptop, use a blank IP address to listen for any incoming connections, 9999 is the "password"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999))
server.listen(1)

#connection and address sent after the connection is established, conn sends/receives data, addr is computer address 
conn, addr = server.accept()

while True:
    #receive data from the laptop, decode it, and strip any spaces
    data = conn.recv(1024).decode().strip()
    #split the data by \n, this way multiple commands don't get mixed up 
    for line in data.split('\n'):
        if not line:
            continue
        #split at every comma
        parts = line.split(",")
        a,b,c = map(float, parts)
        motor_a.on(SpeedDPS(a))
        motor_b.on(SpeedDPS(b))
        motor_c.on(SpeedDPS(c))
        print(motor_a.speed*3)
    
        

    
    

    