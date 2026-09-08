# AP_personal_project_eCVT
Model of Toyota's hybrid transmission, known as the eCVT (electronic continuously variable transmission). The mechanism was primarily built using LEGO Technic and LEGO Mindstorms. 

## Hardware
### Mechanical Parts description: 
 - 4 11x11 Quarter Gear Rings were used to assemble the ring gear, a connector hub with three axles (120 degrees apart) was used to transfer ring gear rotation into an axle rotation. Axle is connected to drive wheel via a 1:5 gear reduction.
 - 60 tooth turntable (piece with hole in middle, where axle connecting to sun gear lies) was used to power the carrier. It is meshed with a twelve tooth gear. 
 - Carrier consists of axle connectors with pin holes for gears, used axles and connectors instead of technic beams due to gear size limitations.
 - Sun is a 36 tooth gear, planets consist of a 16 tooth gear and a 36 tooth gear (due to gear size limitations)
 - Technic Liftarm frames make up most of the structure.
 - Small flat-4 engine model connected to Engine motor (could not use an inline-4 model due to piece and size limitations).
 - Final drive wheel uses a 1:5 gear reduction from the ring gear axle. 

### Electrical/Control Components:
 - Medium ev3 motor used for MG1, 12:20 tooth ratio between MG1 and axle connecting to sun gear, so MG1 has more torque, which is needed due to Lego tolerances and static friction.
 - 2 Large ev3 motors used for MG2 and the Engine.
 - Color Sensor used for gas/brake joystick, created using .reflected_light_intensity attribute. As joystick lever gets closer, reflected light has a larger intensity.
 - Mindstorms ev3 brick used with a flashed SD card that holds an [ev3dev-stretch boot image](https://www.ev3dev.org/downloads/).
 - Built in PID controllers allow motors to maintain speed regardless of driven wheel resistance.

## Kinematics Equations

### Theoretical Equation

The kinematic equation for a standard planetary gear set, known as the **Willis Equation**, is:

$$(1+k)\omega_C = \omega_S + k\omega_R$$

Where:
- $k$ = ratio of ring gear teeth to sun gear teeth
- $\omega_C$ = carrier angular velocity
- $\omega_S$ = sun angular velocity
- $\omega_R$ = ring angular velocity

#### Calculating the K Factor

$$k = \frac{\text{Ring teeth}}{\text{Sun teeth}} = \frac{140}{36} = 3.889$$

#### Gear Ratios and Coefficients

Since the motors and engine are not directly connected to the planetary gears, we must account for intermediate gear reductions:

| Component | Gear Ratio | Calculation | Value |
|-----------|-----------|-------------|-------|
| MG1 → Sun | Input reduction | $-\frac{12}{20}$ | $-0.6$ |
| Engine → Carrier | Input reduction | $\frac{12}{60}$ | $0.2$ |
| MG2 → Ring | Input reduction | $\frac{24}{40}$ | $0.6$ |

*Note: MG1 ratio is multiplied by -1 because there are 2 planet gears*

#### Substituting into Willis Equation

$$(1 + k) \cdot b \cdot \text{ENGINE} = a \cdot \text{MG1} + k \cdot c \cdot \text{MG2}$$

Substituting known values:

$$(1 + 3.889) \cdot 0.2 \cdot \text{ENGINE} = -0.6 \cdot \text{MG1} + 3.889 \cdot 0.6 \cdot \text{MG2}$$

#### Simplified Constraint Equation

$$0 = -0.6 \cdot \text{MG1} - 0.9778 \cdot \text{ENGINE} + 2.334 \cdot \text{MG2}$$

This represents a plane in 3D space with coordinates $(\text{MG1}, \text{ENGINE}, \text{MG2})$ and normal vector:

$$\vec{n_{\text{theory}}} = \langle -0.6, -0.9778, 2.334 \rangle$$

---

### Empirical Model

Empirical data on angular velocity was collected by systematically varying motor speeds and measuring the resulting third motor speed. This data was processed through least squares regression to establish an empirical model.

#### Regression Analysis

Using numpy's least squares algorithm (`lstsq()`), the empirical constraint equation is:

$$-0.4425 = -0.2605 \cdot \text{MG1} - 0.2506 \cdot \text{ENGINE} + \text{MG2}$$

Rearranged:

$$0 = -0.2605 \cdot \text{MG1} - 0.2506 \cdot \text{ENGINE} + \text{MG2} + 0.4425$$

The empirical normal vector is:

$$\vec{n_{\text{empirical}}} = \langle -0.2605, -0.2506, 1 \rangle$$

**Regression Quality:** $R^2 = 0.997$ (99.7% of variance explained)

---

### Theoretical vs. Empirical Comparison

#### Vector Comparison

To compare the two models, we normalize the theoretical vector by dividing by its largest component:

$$\vec{n_{\text{theory}}} = \langle -0.6, -0.9778, 2.334 \rangle$$

$$\vec{n_{\text{theory, normalized}}} = \frac{\vec{n_{\text{theory}}}}{2.334} = \langle -0.257, -0.420, 1 \rangle$$

**Observation:** The empirical vector shows the engine has less influence than theory predicts, likely due to mechanical friction and gear lash.

#### Angle Between Vectors

To measure how closely the models agree, we calculate the angle between the normal vectors:

$$\vec{n_{\text{theory}}} \cdot \vec{n_{\text{empirical}}} = (-0.6)(-0.2605) + (-0.9778)(-0.2506) + (2.334)(1) = 2.736$$

$$|\vec{n_{\text{theory}}}| = \sqrt{0.6^2 + 0.9778^2 + 2.334^2} = 2.766$$

$$|\vec{n_{\text{empirical}}}| = \sqrt{0.2605^2 + 0.2506^2 + 1^2} = 1.032$$

$$\theta = \arccos\left(\frac{2.736}{2.766 \times 1.032}\right) = 8.446°$$

#### Conclusion

The theoretical and empirical models differ by only **8.4 degrees**, indicating excellent agreement between the mathematical model and the physical system. The small discrepancy is attributable to mechanical constraints such as friction, gear tolerance, and backlash in the LEGO mechanism.

---

## Software

### Code File Descriptions (Latest file first):

 - **ev3controller.py:** A standalone control code file using color sensor joystick, combining most of the functionality from ev3side.py and laptopside.py. Allows direct control without network connection.

 - **ev3side.py and laptopside.py:** Two files that communicate via sockets. The EV3 has limited processing power, so the laptop handles data analysis and visualization while the EV3 handles motor control. A tkinter GUI on the laptop displays real-time telemetry.

 - **data_analysis.py:** Processes empirical data from data_farm scripts and uses numpy's `lstsq()` to establish the plane equation relating MG1, MG2, and ENGINE speeds.

 - **data_farm_1.py and data_farm_2.py:** Data collection scripts that vary two motor speeds, record the resulting third motor speed, and log angular velocity measurements to CSV files for regression analysis.

---

## Issues and Updates

### Current Issues (by file):

 - **ev3controller.py:** Needs socket connection to laptop for real-time data graphs
 - **ev3controller.py:** Acceleration ramp-up could be smoother
 - **ev3controller.py:** Battery voltage model needed for increased accuracy
 - **laptopside.py:** Battery discharge model isn't accurate
 - **data_farm_2.py:** Need to include all data collection methods

### Recent Updates

 - Fixed mechanical clicking issue by improving ring gear connector and separating parts
 - Introduced ev3controller.py for simplified standalone operation
 - Fixed acceleration smoothness issue in laptopside.py (now delegated to ev3controller.py)
 - Added tkinter GUI interface for laptopside.py with real-time motor speed display
 - Updated kinematic equations: MG1 coefficient now multiplied by -1 due to repositioning (see data_analysis.py for details)
