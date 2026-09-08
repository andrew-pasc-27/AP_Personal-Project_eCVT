# AP_personal_project_eCVT
Personal Project recreating ecvt from LEGO Mindstorms. 


Model of Toyota’s hybrid transmission, known as the eCVT (electronic continuously variable transmission). The mechanism was primarily built using LEGO Technic and LEGO Mindstorms. 

## Hardware:
### Mechanical Parts description: 
 - 4 11x11 Quarter Gear Rings were used to assemble the ring gear, a connector hub with three axles (120 degrees apart) was used to transfer ring gear rotation into an axle rotation. Axle is connected to 40 tooth gear, which is reduced to a 24 tooth gear when connected to mg2. 
 - 60 tooth turntable (piece with hole in middle, where axle connecting to sun gear lies) was used to power the carrier. It is meshed with a twelve tooth gear. 
 - Carrier consists of axle connectors with pin holes for gears, used axles and connectors instead of technic beams due to gear size limitations.
 - Sun is a 36 tooth gear, planets consist of a 16 tooth gear and a 36 tooth gear (due to gear size limitations)
 - Technic Liftarm frames make up most of the structure.
 - Small flat-4 engine model connected to Engine motor (could not use an inline-4 model due to piece and size limitations).
 - Final drive wheel uses a 1:5 gear reduction from the ring gear axle. 
###   
 - Medium ev3 motor used for MG1, 12:20 tooth ratio between MG1 and axle connecting to sun gear, so MG1 has more torque, which is needed due to Lego tolerances and static friction.
 - 2 Large ev3 motors used for MG2 and the Engine.
 - Color Sensor used for gas/brake joystick, created using .reflected_light_intensity attribute. As joystick lever gets closer, reflected light has a larger intensity.
 - Mindstorms ev3 brick used with a flashed SD card that holds an [ev3dev-stretch boot image](https://www.ev3dev.org/downloads/).
 - Built in PID controllers allow motors to maintain speed regardless of driven wheel resistance.

## Software:
### Code File descriptions (Latest file first):
 - ev3controller.py: A standalone control code file using color sensor joystick, combining most of the functionality from [ev3side.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3side.py) and [laptopside.py](laptopside.py). Uses regression equation from [data_analysis.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_analysis.py). The joystick allows for a non-constant acceleration for improved model accuracy, for example, the engine turns on when pedal is floored, regardless of speed. Added ev3 display functionality, which displays drive gear (reverse, neutral, drive), speed, and measured voltage of the ev3 battery. Ev3 button functionality introduced, using up, middle, and down buttons for drive gear; left and right buttons used for emergency brake. Encountered runtime issues due to ev3 limited functionality, which was solved by updating the display and checking the battery less.

 - ev3side.py and laptopside.py: Two files that are connected using sockets. Due to limited functionality of ev3, I separated the ev3 and laptop so a GUI could be introduced. To connect, the ev3 is booted up and it runs its code file (after being plugged in and establishing an IP) and waits for a connection from another device (the laptop). The laptop looks for the ev3’s IP address and establishes a connection once found. After the connection is made, the interface waits for a press of the gas button/brake buttons. It calculates the mg1/mg2/engine speeds based on the current speed and wanted speed using the regression equation from [data_analysis.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_analysis.py), then packages these speeds and sends them to the ev3. After the payload is sent, the ev3 applies these angular velocities to the motors. There's also a relatively accurate battery depletion model built in (I’m currently unaware of actual battery dynamics in Toyotas, which likely vary by model), where the engine has to turn on to charge the "battery" after it gets to ~25%. Lastly, a sport/normal/eco mode selection and a drive gear shifter: r + n + d was added for added realism.

 - data_analysis.py: This code file takes the results from data_farm_1.py and data_farm_2.py and uses numpy’s least squares algorithm (lstsq()) to establish a plane equation between mg1, mg2, and the engine. R^2 of 99.7. 

 - data_farm_1.py and data_farm_2.py: These code files control the speeds of two motors and to see the resulting speed of the third, collecting angular velocity data of all three and storing them. [CSV of data](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/eCVT%20spreadsheet%20-%20Sheet%201.csv).

## Issues and Updates
### Current issues (by code file):
 - ev3controller.py: needs socket connection to laptop for data graphs
 - ev3controller.py: needs smoother acceleration
 - ev3controller.py: needs ecvt battery model for increased accuracy
 - laptopside.py: battery model isn't accurate
 - data_farm_2.py: include all methods to get data

### Newest updates:
 - Fixed clicking issue with mechanism, by improving ring connector and separating parts. 
 - ev3controller.py introduced
 - laptopside.py acceleration issue has been fixed by using ev3controller.py
 - tkinter interface introduced for laptopside.py
 - kinematic equation changed due to positioning of the engine and MG1, the coefficient is now multiplied by -1 (thought you should know, since data_analysis has been changed a bit for this)

