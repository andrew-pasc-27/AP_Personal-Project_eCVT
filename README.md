# AP_personal_project_eCVT
Model of Toyota's hybrid transmission, known as the eCVT (electronic continuously variable transmission). The mechanism was primarily built using LEGO Technic and LEGO Mindstorms EV3.

## Navigating Main Folders
|Folder|Contents|
|--------|--------|
|**Code Files**|All code files, split into Laptop, Analysis, and EV3 files|
|**Data**|CSV file with empirical data|
|**Media**|Includes all photo media|


## Video Demonstration Links
 - [Demonstration of eCVT](https://drive.google.com/file/d/1AhYpI9F_Cd5zOatm2PwSbGdc_tSj70io/view?usp=share_link)
 - [Demonstration of Motor Data Visualization](https://drive.google.com/file/d/15FJaNPaWlunaGZE18toF5-Q3PvSbY2L1/view?usp=share_link)

## Contents
 - [Hardware](#hardware)
 - [Kinematics Equations](#kinematics-equations)
 - [Software](#software)
 - [Updates](#updates)

## Hardware
### Mechanical Parts description: 
 - 4 11x11 Quarter Gear Rings were used to assemble the ring gear, a connector hub with three axles (120 degrees apart) was used to transfer ring gear rotation into an axle rotation. Axle is connected to the ring gear through a 60 tooth turntable.
 - 60 tooth turntable (piece with hole in middle, where axle connecting to sun gear lies) was used to power the carrier. It is meshed with a twelve tooth gear. 
 - Carrier consists of axle connectors with pin holes for gears, used axles and connectors instead of technic beams due to gear size limitations.
 - Sun is a 36 tooth gear, planets consist of a 16 tooth gear and a 36 tooth gear (due to gear size limitations)
 - Technic Liftarm frames make up most of the structure.
 - Small flat-4 engine model connected to Engine motor (could not use an inline-4 model due to piece and size limitations).

### Electrical/Control Components:
 - Mindstorms EV3 brick used as central control device.
 - Medium EV3 motor used for MG1, 12:20 tooth ratio between MG1 and axle connecting to sun gear, so MG1 has more torque, which is needed due to Lego tolerances and static friction.
 - 2 Large EV3 motors used for MG2 and the Engine. MG2 has a 24:40 tooth ratio with the ring gear axle, and Engine has a 12:60 ratio with carrier gear.
 - Color Sensor used for gas/brake joystick.
 - Built in PID controllers allow motors to maintain speed regardless of driven wheel resistance.

## Kinematics Equations
 - [The Theoretical Equation](#simplified-constraint-equation)
 - [The Empirical Equation](#regression-equation-analysis)
 - [Comparison](#vector-comparison)

### Finding Theoretical Equation

The kinematic equation for a standard planetary (epicyclic) gear set, known as the **Willis Equation**, is:

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

Empirical data on angular velocity was collected by systematically varying motor speeds and measuring the third motor speed. This data was processed through least squares regression to establish a constraint equation relating motor speeds.

#### Regression Equation Analysis

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

**Observation:** The empirical vector shows the engine has less influence on the final output than theory predicts, likely due to mechanical friction and gear path.

#### Angle Between Vectors

To measure how closely the models agree, we calculate the angle between the normal vectors:

$$\vec{n_{\text{theory}}} \cdot \vec{n_{\text{empirical}}} = (-0.6)(-0.2605) + (-0.9778)(-0.2506) + (2.334)(1) = 2.736$$

$$|\vec{n_{\text{theory}}}| = \sqrt{0.6^2 + 0.9778^2 + 2.334^2} = 2.766$$

$$|\vec{n_{\text{empirical}}}| = \sqrt{0.2605^2 + 0.2506^2 + 1^2} = 1.032$$

$$\theta = \arccos\left(\frac{2.736}{2.766 \times 1.032}\right) = 8.446°$$

#### Conclusion

The theoretical and empirical models differ by only **8.4 degrees**, meaning the theoretical and empirical models are very similar. The small discrepancy can be attributed to mechanical constraints and friction losses in the system.

---

## Software

### Code File Descriptions (Latest file first):

 - **[ev3controller_with_sockets.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3controller_with_sockets.py)** and **[laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/laptop_to_ev3controller.py):** Control code that establishes socket connection between laptop and EV3 brick, allowing real-time telemetry visualization on the laptop while the EV3 runs the eCVT simulation.

 - **[ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3controller.py):** A standalone control code file using color sensor joystick, combining most of the features from the socket-based implementation without requiring a laptop connection.

 - **[ev3side.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3side.py)** and **[laptopside.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/laptopside.py):** Original socket-based control implementation with separate files for EV3 and laptop communication.

 - **[data_analysis.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_analysis.py):** Processes empirical data from data_farm scripts and uses numpy's `lstsq()` to estimate constraint plane coefficients for the empirical model.

 - **[data_farm_1.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_farm_1.py)** and **[data_farm_2.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_farm_2.py):** Data collection scripts that systematically vary motor speeds and record resulting angular velocities for empirical analysis.

### Libraries:
| Library | Type | Purpose |
|-----------|-----------|------------------------|
| `Numpy` | Data Analysis | Allowed for [regression analysis](#regression-equation-analysis) of empirical data |
| `Matplotlib` | Data Visualization | Allows for real time motor data visualization in [laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/laptop_to_ev3controller.py) |
| `Ev3Dev2` | Mindstorms Control | Allows python script to communicate with EV3 components |
| `Socket` | Networking | Allows computer and EV3 to connect over a low-level interface |
| `Tkinter` | User Interface | Allows for real user interface that improves experience |
| `Time` | Standard Library | Allows set intervals for when EV3 should run |

### Software Implementations:

 - **Color Sensor Joystick:** Using `.reflected_light_intensity` attribute, an EV3 color sensor was used for the gas/brake joystick. As the joystick lever moves closer to the sensor, the intensity increases, allowing for analog control input.

 - **Laptop and EV3 connection:** Used Socket library. The EV3 runs its code file, setting up a socket server and listening for any connection requests. Concurrently, the laptop initializes its socket client and connects to the EV3's server, allowing bidirectional communication for telemetry and control.

---

## Updates

### Future Updates (by file):
 - **[laptopside.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/laptopside.py):** Battery discharge model isn't accurate
 - **[data_farm_2.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/data_farm_2.py):** Need to include all data collection methods

### Recent Updates (Latest first)

 - Introduced [ev3controller_with_sockets.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3controller_with_sockets.py) and [laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/laptop_to_ev3controller.py) for improved socket-based control with real-time visualization
 - Reduced runtime between iterations by improving LCD display dynamics.
 - Fixed mechanical clicking issue by improving ring gear connector and separating parts
 - Introduced [ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3controller.py) for standalone operation
 - Updated battery and acceleration models for increased accuracy (though not perfect)
 - Updated kinematic equations: MG1 and Engine coefficient now multiplied by -1 due to motor and gear repositioning.
