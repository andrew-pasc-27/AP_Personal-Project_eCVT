# AP_personal_project_eCVT
Personal Project recreating ecvt from LEGO Mindstorms. 

Disclaimers:
 - this is a model of Toyota’s ecvt, so variable names correspond to ecvt parts (mg1, engine, mg2).
 - Mg1 uses a medium ev3 motor, while the engine and mg2 use large motors
 - ev3dev-stretch was used to make the ev3 support python.
 - All speeds are in w, or angular velocity, which makes data nice and consistent and also matches well with online planetary gear set equations.

Current issues (by code file):
 - ev3controller.py: needs socket connection to laptop for data graphs
 - ev3controller.py: needs smoother acceleration/more believable acceleration
 - ev3controller.py: needs ecvt battery model for increased accuracy
 - laptopside.py: battery model isn't really accurate, acceleration is still constant (therefore it kinda sucks)
 - data_farm_2.py: I didn't include all the ways I got data so the numbers I got might be confusing

Newest updates:
 - fixed clicking issue with mechanism, pretty smooth 😁
 - ev3controller.py introduced, check description below
 - laptopside.py acceleration issue has been fixed by using ev3controller.py (pro tip: if there's a problem just make a new thing to avoid it)
 - tkinter interface introduced for laptopside.py
 - kinematic equation changed due to positioning of the engine, the coefficient is now multiplied by -1 (thought you should know, since data_analysis has been changed a bit for this)


Code file descriptions (latest file first):
 - ev3controller.py (I really need more creative names 🙃): A standalone control code file (FINALLY NO LAPTOP!). A color sensor was used to create a forward/back joystick using built in .reflected_light_intensity attribute. It returns a value from 0-100, and right now 47 is the middle value (higher than 47 accelerates, less than decelerates). It's pretty accurate, and a nice fix because acceleration isn't constant, and I can calculate when the engine should turn on (unlike laptopside.py). Also, the speed, battery percentage of ev3, and drive gear are displayed on the ev3 itself. The code file looks much nicer compared to other ones because I was advised to keep constants defined at the top and functionally abstract any repeated parts so the code's easier to understand and read. Surprisingly, making it and debugging it was a lot easier because even I could read it better (noted for future). I also used a try/except/finally, which is a first (I've never used finally before, thought I might as well try). 

 - ev3side.py and laptopside.py: Two files. One goal. (wow was that motivating or what) Anyway, because ev3dev2 is limited to basic libraries, any attempt at making a GUI or even using numpy (check out data_analysis.py) was a fat no (It won't even use f-strings 😭). So, I had to separate the laptop and ev3 so I could introduce some higher level libraries. The ev3 and laptop are connected using sockets, essentially the ev3 is booted up and it runs its code file (after being plugged in and establishing an IP) and waits for a connection from another device (the laptop). The laptop looks for the ev3’s IP address and establishes a connection once found. After that, laptopside.py's GUI (super cool interface btw) waits for a press of the gas button/brake buttons. It calculates the mg1/mg2/engine speeds based on the current speed and wanted speed, then packages them and sends them to the ev3. Pretty cool. After the payload is sent, the ev3 just runs it. There's also a somewhat accurate (not really) battery depletion model in it, where the engine has to turn on to charge the "battery" after it gets to ~25%. Lastly, a sport/normal/eco mode selection and a drive gear shifter: r + n + d (no park because it doesn't really move) was added for coolness.

 - data analysis uses numpy’s least squares algorithm (lstsq()) to establish a relationship between each speed, so mg1, engine, and mg2. Its result is then copy-and-pasted into laptopside.py

 - data farms 1 and 2 both run tests on my ecvt, collecting data on each 3 motors speed in order to establish a relationship
  





 
