# AP_personal_project_eCVT
Three motor model of Toyota's hybrid transmission, known as the eCVT (electronic continuously variable transmission). The mechanism was primarily built using LEGO Technic and LEGO Mindstorms EV3. 

**Key Results**
- Theoretical vs. improved empirical models differ by only **8.4°**
- Least-squares regression: **R² = 0.997**
- Full loop: mechanical build → theoretical kinematics → empirical validation → custom PID control

## Navigating Main Folders
|Folder|Contents|
|--------|--------|
|**Code Files**|All code files, split into Laptop, Analysis, and EV3 files|
|**Data**|CSV file with empirical data|
|**[requirements.txt](requirements.txt)**|Project Dependecies|

## Contents
 - [Hardware](#hardware)
 - [Kinematics Equations](#kinematics-equations)
 - [Software](#software)
 - [Updates](#updates)
 - [Purpose, Takeaway, and Initial Methodology](#personal-journey)
 - [Photo and Video Demonstrations](#photo-and-video-demonstrations)


## Hardware
### Full Model View
<img width="4284" height="5712" alt="IMG_8246" src="https://github.com/user-attachments/assets/360ac9b0-39a1-4811-b689-6709ddd8f0af" />
*Includes eCVT Model (back), Mindstorms control unit (front left), Joystick (front right)*

### Planetary Gearset
<details>
 <summary>Click to View Close Up Photos</summary>

 | Ring Gear | Carrier + Sun Gear |
 |-----------|--------------------|
 | <img src="https://github.com/user-attachments/assets/dbfd965f-d79c-4fea-9212-91a023d91ba7" width="320" alt="Ring gear close-up"> | <img   src="https://github.com/user-attachments/assets/7fe5148b-204e-41c8-8000-58254cd7af67" width="320" alt="Carrier and sun gear"> |
</details>

- **Ring gear**: Built from four 11×11 quarter gear rings. A three-axle hub (120° spacing) transfers rotation to the output.
- **Carrier & Sun**: Carrier uses axle connectors instead of beams due to gear size limits. Sun is a 36-tooth gear; planets are 16T + 36T. A 60-tooth turntable drives the carrier.
  
<details>
 <summary>Click to see Overall Structure</summary>
 
 ### Overall Structure
 <img width="3024" height="4032" alt="IMG_2173" src="https://github.com/user-attachments/assets/2ff1d231-59b6-4461-b359-9f594a41b05d" />
 *MG1 and Engine on the left, MG2 on the right. Technic liftarm frame with a small flat-4 engine model.*
</details>


### Electrical / Control Components
- EV3 brick as the central controller
- Medium motor for MG1 (12:20 reduction for higher torque)
- Two large motors for MG2 and Engine (24:40 and 12:60 reductions)
- Custom PID controller keeps motor speeds stable under load
- Custom color-sensor pedal box for analog throttle input
<details>
 <summary>Click to View Pedal Box Close Up</summary>
 
 | Pedal Box Exterior | Pedal Box Interior |
 |-------------------|-------------------|
 |<img width="4284" height="5712" alt="IMG_8263" src="https://github.com/user-attachments/assets/6ba5354e-c82d-4b05-8ee4-c4ddfdf1fd3d" width="220" /> | <img width="3024" height="4032" alt="IMG_8262" src="https://github.com/user-attachments/assets/03038eda-2a97-43de-aa69-d8803fad6ac8" width="220"/> |
</details>

## Kinematics Equations
 - [The Theoretical Equation](#simplified-theoretical-equation)
 - [Simple Empirical Model](#simple-empirical-model)
 - [The Empirical Equation](#improved-empirical-model)
 - [Comparison](#vector-comparison)

### The Theoretical Equation
<details>

  <summary>Click to View Methodology</summary>
  
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

</details>


#### Simplified Theoretical Equation

$$0 = -0.6 \cdot \text{MG1} - 0.9778 \cdot \text{ENGINE} + 2.334 \cdot \text{MG2}$$

This represents a plane in 3D space with coordinates $(\text{MG1}, \text{ENGINE}, \text{MG2})$ and normal vector:

$$\vec{n_{\text{theory}}} = \langle -0.6, -0.9778, 2.334 \rangle$$

---

### The Empirical Models

Empirical data on angular velocity was collected by systematically varying motor speeds and measuring the third motor speed. 

#### Simple Empirical Model
A more accurate equation relating the motor speeds can be derived by taking the cross product of any two angular velocity vectors in the empirical dataset that are not collinear and not $(0,0,0)$. <br>
*The cross product will output a normal vector which can be translated into a 3D plane*

I will use the coordinates $(-159, -107, -78)$ and $(615, 250, 215)$, which can be represented as this matrix:

$$
\begin{vmatrix}
\mathbf{i} & \mathbf{j} & \mathbf{k} \\
-159 & -107 & -78 \\
615 & 250 & 215
\end{vmatrix}
$$

*Since* $(0,0,0)$ *exists for this gearset, it can be assumed as the starting point for both vectors. Therefore, each coordinate also represents a vector.*

Taking the cross product of these vectors:
 
$$\langle -23005 + 19500, -47970 + 34185, -39750 + 65805 \rangle$$

**Normal Vector derived from cross products**: 

$$\vec{n_{\text{simple}}} = \langle -3505, -13785, 26055 \rangle$$

**Simple Empirical Equation:**

$$0 = -3505 \cdot \text{MG1} - 13785 \cdot \text{ENGINE} + 26055 \cdot \text{MG2}$$ <br>
*Used* $(0,0,0)$ *as starting point, assumed coordinates of* $(\text{MG1}, \text{ENGINE}, \text{MG2})$ *.*

---

#### Improved Empirical Model
The accuracy of the model can be improved by relating all vectors. By processing the data through the least squares regression, a constraint equation relating motor speeds can be established.

Using numpy's least squares algorithm (`lstsq()`), the empirical constraint equation is:

$$-0.4425 = -0.2605 \cdot \text{MG1} - 0.2506 \cdot \text{ENGINE} + \text{MG2}$$

Rearranged:

$$0 = -0.2605 \cdot \text{MG1} - 0.2506 \cdot \text{ENGINE} + \text{MG2} + 0.4425$$

The empirical normal vector is:

$$\vec{n_{\text{improved}}} = \langle -0.2605, -0.2506, 1 \rangle$$

**Regression Quality:** $R^2 = 0.997$ (99.7% of variance explained)

---

### Theoretical vs. Empirical Comparison
<details>
  <summary>Click to View Methodology</summary>
 
  #### Vector Comparison
 
  To compare the three models, we normalize the normal vectors by dividing by their largest component:
  
  $$\vec{n_{\text{theory}}} = \langle -0.6, -0.9778, 2.334 \rangle$$
  
  $$\vec{n_{\text{theory, normalized}}} = \frac{\vec{n_{\text{theory}}}}{2.334} = \langle -0.257, -0.420, 1 \rangle$$


  $$\vec{n_{\text{simple}}} = \langle -3505, -13785, 26055 \rangle$$
  
  $$\vec{n_{\text{simple, normalized}}} = \frac{\vec{n_{\text{simple}}}}{26055} = \langle -0.134, -0.52, 1 \rangle$$

  $$\vec{n_{\text{improved}}} = \langle -0.2605, -0.2506, 1 \rangle$$ <br>
  *No need for normalization*
  
  **Observation:** The simplified empirical vector shows that MG1 has less influence on the final output than theory predicts, but the improved empirical vector shows that the engine has less influence than theory predicts. The simplified empirical model sees variance likely due to sample bias; the improved model varies likely due to mechanical friction and gear path. *It is worth noting that the regression saw an* $R^2 = 0.997$ *, which makes the variance between the simplified and improved models surprising.*
  
  #### Angle Between Vectors
  *For this comparison, I will only use the theoretical and improved model, due to simplified model variance.*
  To measure how closely the theoretical and improved empirical models agree, we calculate the angle between the normal vectors:
  
  $$\vec{n_{\text{theory}}} \cdot \vec{n_{\text{empirical}}} = (-0.6)(-0.2605) + (-0.9778)(-0.2506) + (2.334)(1) = 2.736$$
  
  $$|\vec{n_{\text{theory}}}| = \sqrt{0.6^2 + 0.9778^2 + 2.334^2} = 2.766$$
  
  $$|\vec{n_{\text{empirical}}}| = \sqrt{0.2605^2 + 0.2506^2 + 1^2} = 1.032$$
  
  $$\theta = \arccos\left(\frac{2.736}{2.766 \times 1.032}\right) = 8.446°$$

</details>

#### Conclusion

The engine motor has less influence on the final output than theory suggests. However, the theoretical and improved empirical models differ by only **8.4 degrees**, with the engine accounting for most of the difference. The small discrepancy can be attributed to mechanical constraints and friction losses in the system. <br>
The simplified model saw surprising variance (over $$15°$$ of difference over improved; so it was not included in the final comparison). It is an example of sample bias but also reveals some inconsistencies in the data that the improved model aims to mitigate. 

**Graph of Plane Equations:**
<img width="1023" height="636" alt="Screenshot 2026-10-28 at 10 32 52 AM" src="https://github.com/user-attachments/assets/c3f8a058-8445-47ed-8bd9-dfb23697d9de" />

*Where the blue plane represents the theoretical equation and the red plane represents the improved empirical equation*


---

## Software

### Code File Descriptions (Latest file first):

 - **[new_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/ev3/new_ev3controller.py):** Added new Engine class, which properly determines the engine speed based off multiple cost functions. Added custom PID controller for insight and proper tuning for my transmission. Creep function and a more accurate hybrid model have also been added.

 - **[ev3controller_with_sockets.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/ev3/ev3controller_with_sockets.py)** and **[laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/laptop/laptop_to_ev3controller.py):** Control code that establishes socket connection between laptop and EV3 brick, allowing real-time telemetry visualization on the laptop while the EV3 runs the eCVT simulation.

 - **[ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/ev3controller.py):** A standalone control code file using color sensor joystick, combining most of the features from the socket-based implementation without requiring a laptop connection.

 - **[ev3side.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/ev3/ev3side.py)** and **[laptopside.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/laptop/laptopside.py):** Original socket-based control implementation with separate files for EV3 and laptop communication.

 - **[data_analysis.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/analysis/data_analysis.py):** Processes empirical data from data_farm scripts and uses numpy's `lstsq()` to estimate constraint plane coefficients for the empirical model.

 - **[data_farm_1.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/analysis/data_farm_1.py)** and **[data_farm_2.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/analysis/data_farm_2.py):** Data collection scripts that systematically vary motor speeds and record resulting angular velocities for empirical analysis.

### Libraries:
| Library | Type | Purpose |
|-----------|-----------|------------------------|
| `Numpy` | Data Analysis | Allowed for [regression analysis](#regression-equation-analysis) of empirical data |
| `Matplotlib` | Data Visualization | Allows for real time motor data visualization in [laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/laptop/laptop_to_ev3controller.py) |
| `Ev3Dev2` | Mindstorms Control | Allows python script to communicate with EV3 components |
| `Socket` | Networking | Allows computer and EV3 to connect over a low-level interface |
| `Tkinter` | User Interface | Allows for real user interface that improves experience |
| `Time` | Standard Library | Allows set intervals for when EV3 should run |

### Software Implementations:

 - **Color Sensor Pedal Box:** Using `.reflected_light_intensity` attribute, an EV3 color sensor was used for the gas/brake pedal box. A differential allows the gas pedal to move a reflective tile towards the color sensor when pressed, while the brake pedal moves it backwards when pressed. These sensor readings are mapped to acceleration values.

 - **Laptop and EV3 connection:** Used Socket library. The EV3 runs its code file, setting up a socket server and listening for any connection requests. Concurrently, the laptop initializes its socket client and connects to the EV3's server, allowing bidirectional communication for telemetry and control.

---

## Updates

### Future Updates:
 - **[data_farm_2.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/analysis/data_farm_2.py):** Need to include all data collection methods

### Recent Updates (Latest first):
 - Introduced Engine class, custom PID controller, updated battery discharge model, creep function.
 - Introduced gas/brake pedal box, no more joystick.
 - Introduced [ev3controller_with_sockets.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/ev3/ev3controller_with_sockets.py) and [laptop_to_ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/laptop/laptop_to_ev3controller.py) for improved socket-based control with real-time visualization
 - Reduced runtime between iterations by improving LCD display dynamics.
 - Fixed mechanical clicking issue by improving ring gear connector and separating parts
 - Introduced [ev3controller.py](https://github.com/andrew-pasc-27/AP_Personal-Project_eCVT/blob/main/code%20files/ev3/ev3controller.py) for standalone operation

---

## Personal Journey
### Purpose
From reading through my first *Car and Driver* magazine to experiencing Forza Horizon 4 on my racing simulator, I’ve been obsessed with cars. Seeing the simplicity and smoothness of the eCVT in real life as a young driver, I began delving into the world of transmissions. I realized the only way to grasp the structure was to build it myself with the many LEGOs I acquired as a child, another childhood obsession of mine.

### Takeaways
First and foremost, I want to thank you if you made it this far. This project was one of the most fun and tiring projects I’ve taken on in the past few years, and the fact that another person has read this and likely shares my interest makes me feel happy (so thanks 🤗).

**My takeaways**: 
- Do that project you’ve always wanted to do: I could only take in so much from a video, and I’ve wanted to build my own transmission for a while. I put it off for a while (personal commitments among other things), but I’m glad I started the project. I wish I had more time to really tinker with the project, so if you want to do something, just do it.
- Sample bias is real: considering the mechanical link of the motors, I didn’t expect much sample bias when constructing my initial empirical model. I was quite surprised when the simple model varied more than the theoretical model did from the final empirical model. Always check your work and don’t assume everything always works because you tested it once.
- Control matters just as much as the mechanism: Controlling the output was just as hard as creating the initial mechanism. I have come a lot more appreciative of all the work that goes in to creating a transmission and have become more intrigued at building one myself (whether from the control side or the mechanical side).
- Always have fun: Just have fun. I allowed my inner self loose with this project, which made it that much more enjoyable. You should too.

### Failures and Iterations
A project wouldn't be much of a project without something going wrong. A few things that went wrong and were fixed:

- **Mechanical binding and clicking:**
  In my initial model, the carrier and planet gears often collided with the ring gear holder at high speeds. I updated the carrier and made the ring holder thinner so the parts could be spaced apart.    There was also a clicking noise every revolution of the carrier, which was solved through a stronger frame.
- **Theoretical and Simple Models:**
  My initial theoretical model did not account for the differing gear ratios that arose due to the gear reductions I put in place; this made it very inaccurate. My simple empirical model using the cross product two angular velocity vectors outputted a plausible normal vector, but it was more inaccurate than the corrected theoretical model. I updated this using a least squares regression.
- **Battery and acceleration models:**
  Early models were too sensitive or were not accurate to how a real car responds. Code has been updated since then to more accurately model a hybrid vehicle.

### Methodology
#### Creating the gearset
The gearset needs three items:
- sun gear
- planet gear(s)
- ring gear

*Tip: Find your ring and sun first, then find planets that mesh*

Use a gear with a hole in the middle to allow two inputs to converge at a single point, or connect the motor directly to the ring. 
Add a lot of structure around the gearset to avoid breaking at high speed. 

#### Adding Control functionality
Once the gearset is created, add your motors of choice to the structure.
*I recommend Mindstorms*

For EV3 users:
- Download the ev3dev-stretch image and use a flasher of your choice to flash this image onto a miniSD card (2-32 GB)
- Insert this miniSD card into the EV3 and boot it. Connect it to your computer and download VSCode.
- On VSCode, download the ev3dev extension and begin coding using the correct imports.
- When ready to run, press *Run and Debug*, then allow the EV3 to connect to your computer.
- Have fun!

---

## Photo and Video Demonstrations

### All Photos

  
  |File Name|Description|Photo|
  |----------|--------------|----------------|
  |Full_view.JPG|Picture of full project|<img width="90" height="120" alt="IMG_8246" src="https://github.com/user-attachments/assets/360ac9b0-39a1-4811-b689-6709ddd8f0af" width="90"/>|
  |eCVT_front_view.JPG|Front view of the mechanism|<img width="90" height="120" alt="IMG_2173" src="https://github.com/user-attachments/assets/2ff1d231-59b6-4461-b359-9f594a41b05d" width="90"/>|
  |eCVT_left_view.JPG|Left view of the mechanism|<img width="90" height="120" alt="ECVT_left_view" src="https://github.com/user-attachments/assets/4f8d7d72-1a10-4868-9f6b-6d7bd4577875" />|
  |eCVT_back_view.JPG|Back view of the mechanism|<img width="90" height="120" alt="eCVT_back_view" src="https://github.com/user-attachments/assets/8e78ad91-a22c-4818-8b79-ff36b4c4b2e9" />|
  |eCVT_right_view.JPG|Right view of the mechanism|<img width="90" height="120" alt="eCVT_right_view" src="https://github.com/user-attachments/assets/c6452538-fc94-4ad7-99c1-72d50bbb75eb" />|
  |right_side_close_up.JPG|Close up of the right side structure|<img width="90" height="120" alt="right_side_close_up" src="https://github.com/user-attachments/assets/13c59920-17eb-452d-b5d9-875dd8b3429b" />|
  |left_side_close_up.JPG|Close up of the left side structure|<img width="90" height="120" alt="left_side_close_up" src="https://github.com/user-attachments/assets/ef02d7a4-33f2-4c7b-b88c-7102d7a607e9" />|
  |Ring+carrier_close_up.JPG|Close up of the inner mechanism|<img height="120" alt="Ring+carrier_close_up" src="https://github.com/user-attachments/assets/3d380b8a-da01-45e8-bfaf-e85455019d15" />|
  |ring_close_up.JPG|Close up of the ring and its holder|<img width="90" height="120" alt="ring_close_up" src="https://github.com/user-attachments/assets/07ff45cf-4b90-40e8-b570-babad686bc97" />|
  |carrier_close_up.JPG|Close up sun and carrier|<img width="90" height="120" alt="carrier_close_up" src="https://github.com/user-attachments/assets/c1188baf-d492-4815-8737-816156f0eb6e" />|
  |pedal_box.JPG|Front view of the pedal box|<img width="90" height="120" alt="IMG_8263" src="https://github.com/user-attachments/assets/2036d9af-c0da-47ed-a56c-f24e809e58f2" />|
  |pedal_box_interior.JPG|Underside of pedal box|<img width="90" height="120" alt="IMG_8262" src="https://github.com/user-attachments/assets/03038eda-2a97-43de-aa69-d8803fad6ac8" width="90"/> |

### Video Demonstration Links
 - [Demonstration of eCVT](https://youtube.com/shorts/jn_OX8D9L44?feature=share)
 - [Demonstration of eCVT with Motor Data Visualization](https://youtube.com/shorts/bhpzd6ihE0Y?feature=share)

