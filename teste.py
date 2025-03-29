import numpy as np
import re

with open('data.txt', 'r') as f:
    # Funcao objetiva
    fn = f.readline().split()
    is_max = (fn[0] == 'max')
    
    # Quantidade de variaveis (x1, x2, ..., xn)
    num_vars = len(re.findall(r'x\d+', fn[3])) 

    # Quantidade de restricoes
    constraints = f.readlines()
    num_ineqs = len(constraints)
    print(f"Numero de restricoes: {num_ineqs}")

    # Quantidade de >= e <=
    num_more_or_equal = len([line for line in constraints if ">=" in line])
    num_less_or_equal = len([line for line in constraints if "<=" in line])
    print(f"Numero de maior ou igual: {num_more_or_equal}")
    print(f"Numero de menor ou igual: {num_less_or_equal}")

    # Extrai os coeficientes da funcao objetivo
    print(fn[3])
    coefficients = np.array(re.findall(r'(-?\d+)\s*\*?\s*x\d+', fn[3]), dtype=float)
    print(coefficients)

    # Constroi a matriz custo
    cost_matrix = np.zeros(num_vars + num_more_or_equal + num_less_or_equal)
    cost_matrix[:len(coefficients)] = coefficients
    print(f"Matriz custo: {cost_matrix}")


