import numpy as np
import re

with open('data.txt', 'r') as f:
    # Objetive function
    fn = f.readline().split()
    if fn[0] == 'max':
        max = True
    else:
        max = False
    
    num_vars = len(re.findall("x[0-9]", fn[3]))

    constraints = f.readlines()
    num_ineqs = len(constraints)
    print(f"Numero de restricoes: {num_ineqs}")

    num_more_or_equal = len([line for line in constraints if ">=" in line])
    num_less_or_equal = len([line for line in constraints if "<=" in line])
    print(f"Numero de maior ou igual: {num_more_or_equal}")
    print(f"Numero de menor ou igual: {num_less_or_equal}")

    num_col = num_vars + num_less_or_equal + num_more_or_equal
    num_lines = num_ineqs

    #print(f"Matriz A: {num_lines}x{num_col}")
    print(fn[3])
    cost_matrix = np.matrix('1, 2, 3, 4')
    print(f"Matriz custo: {cost_matrix}")

    # agora preciso tirar os coeficientes de fn e colocar na matriz custo



