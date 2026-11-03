import numpy as np

df = pd.read_csv("ecvt_angular_velocity_data")

# Extract a, b, c
a_vals = []
b_vals = []  
c_vals = [] 

for index, row in df.iterrows():
    a_vals.append(row["MG1"])
    b_vals.append(row["ENGINE"])
    c_vals.append(row["MG2"])

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


