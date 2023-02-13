import sympy
import numpy as np

if __name__=="__main__":
    c = sympy.symarray("c", (3, 3))
    print(c)
    r1 = np.array([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])
    r2 = np.array([
        [1, 0, 0],
        [0, 0, -1],
        [0, 1, 0]
    ])
    fc = np.matmul(r1, c) - np.matmul(c, r2)
    print(fc)
    sol = sympy.solve(fc.reshape(-1))
    print(sol)