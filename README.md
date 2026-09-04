# AP_personal_project_eCVT
Personal Project recreating ecvt from LEGO Mindstorms. This repository includes all code files made to collect data and connect the ev3 to my Laptop through ev3dev and sockets. 

Disclaimers:
 - this is a model of Toyota’s ecvt, so variable names correspond to ecvt parts.
 - also, mg1 uses a medium ev3 motor, while engine and mg2 use large motors
 - ev3dev-stretch was used to make the ev3 support python.
 - all speeds are taken in w, or angular velocity, makes data nice and consistent and also matches well with online planetary gear set equations

Current issues:
 - Clicking issue with the mechanism… can’t truly pinpoint where it is coming from.
 - laptopside.py has no way to calculate acceleration, button press for adding/subtracting speed has a static magnitude.
 - ev3controller.py: needs socket connection to laptop

Newest updates:
 - tkinter interface introduced for laptopside.py
 - ev3controller.py: color sensor used to create joystick, using built in .reflected_light_intensity attribute, returns a value from 0-100, right now, 40 is the middle value (higher than 40 accelerates, less than decelerates). It’s a nice fix because it allows you to directly modify acceleration, though needs to be configured to talk to the laptop so gui can be used and possibly matlab graphs.
 - updated mechanical strength of ecvt





V1 code file descriptions (commits 1-10):
 - data farms 1 and 2 both run tests on my ecvt, collecting data on each 3 motors speed in order to establish a relationship

 - data analysis uses numpy’s least squares algorithm (lstsq()) to establish a relationship between each speed, so mg1, engine, and mg2. Its result is then copy-and-pasted into laptopside.py

 - ev3side.py and laptopside.py: the reason I separated ev3side and laptop side was for a few reasons, but mainly that I wanted it to be future proof for any revisions, such as an upgrade to an actual interface using pygames or tkinter. Also, many of the normal python libraries, such as numpy, dont exist on ev3 stretch due to its limited functionality, so separating the laptop and ev3 was pretty             necessary for any higher level coding.
They are separated using sockets, essentially the ev3 is booted up and it runs its code file (after being plugged in and     establishing an IP), and then the laptop file is run. The laptop looks for the ev3’s IP address and establishes a connection.
After that, the laptopside code file uses a pretty rudimentary interface (the terminal haha) to ask the user to input a wanted speed, a battery percentage (modeling an actual ecvt, which has limited battery), and a time it has to accelerate in. It then packages this and sends it to the ev3. Pretty cool.
After the payload is sent, the ev3 just runs it.  
