import numpy as np

#lists from data
list1 = [(-150, 0, 52), (-313, 0, 83), (-467, 0, 138), (-620, 0, 171), (-769, 0, 206), (-921, 0, 239), (-957, 0, 239), (-941, 0, 244), (-918, 0, 246), (-943, 0, 241)]
list2 = [(159, 107, -78), (332, 209, -138), (478, 316, -209), (632, 419, -284), (786, 526, -350), (830, 631, -376), (873, 678, -401), (886, 691, -385), (850, 685, -378), (827, 672, -391)]
list3 = [(-149, 104, 0), (-229, 210, 0), (-324, 315, 0), (-441, 422, 0), (-528, 523, 0), (-589, 630, 0), (-685, 718, 0), (-736, 719, 0), (-730, 724, 0), (-700, 720, 0)]
list4 = [(164, 0, -75), (321, 0, -78), (483, 0, -124), (632, 0, -174), (784, 0, -206), (929, 0, -231), (915, 0, -244), (904, 0, -241), (915, 0, -236), (957, 0, -243), (0, 105, -23), (0, 213, -60), (0, 318, -87), (0, 418, -106), (0, 524, -138), (0, 633, -152), (0, 706, -169), (0, 700, -168), (0, 706, -169), (0, 709, -172), (-298, -173, 115), (-615, -250, 215), (-908, -344, 322), (-799, -396, 314), (-1005, -383, 357), (-926, -428, 361), (-949, -389, 347), (-895, -430, 347), (-916, -400, 333), (-883, -417, 323)]
list5 = [(-158, 106, 0), (-313, 208, 58), (-488, 316, 91), (-622, 423, 44), (-788, 529, 71), (-933, 630, 82), (-940, 700, 65), (-940, 699, 66), (-959, 699, 71), (-941, 699, 68)]
data = (list1 + list2 + list3 + list4 + list5)

# Extract a, b, c
a_vals = []
b_vals = []  
c_vals = [] 

for a, b, c in data:
    a_vals.append(a)
    b_vals.append(b)
    c_vals.append(c)

a_vals = np.array(a_vals)
b_vals = np.array(b_vals)
c_vals = np.array(c_vals)

# Linear regression: c = k0 + k1*a + k2, using least squares to solve for [k0, k1, k2]
A_matrix = np.column_stack([np.ones(len(a_vals)), a_vals, b_vals])
coefficients = np.linalg.lstsq(A_matrix, c_vals, rcond=None)[0]

k0, k1, k2 = coefficients
print("Regression equation: mg2 = " + str(k0) + " + " + str(k1) + "*mg1 + " + str(k2) + "*engine")
print("\nCoefficients:")
lst = [k0, k1, k2]
print(lst)

# calculate R-squared
c_predicted = k0 + k1 * a_vals + k2 * b_vals
ss_res = np.sum((c_vals - c_predicted) ** 2)
ss_tot = np.sum((c_vals - np.mean(c_vals)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

print("\nR-squared: " + str(r_squared))


