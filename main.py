import numpy as np
import re
with open('temp.txt', 'r') as f:
    # Salva todo o conteudo do arquivo em uma variavel
    data = f.readlines() 
 
    # Funcao objetiva
    fn = data[0].split()
    is_max = (fn[0] == 'max')
    
    # Quantidade de variaveis (x1, x2, ..., xn)
    num_vars = len(re.findall(r'x\d+', fn[3])) 

    # Quantidade de restricoes
    constraints = data[1:]
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

    # Constroi a matrix b
    b_matrix = np.zeros(len(constraints))
    nums = []
    for constraint in constraints:
        if '<=' in constraint:
            nums.append(constraint.split('<=')[1].strip()) # https://stackoverflow.com/questions/6696027/how-to-split-elements-of-a-list
        elif '>=' in constraint:
            nums.append(constraint.split('>=')[1].strip())
        elif '=' in constraint and not ('<=' in constraint or '>=' in constraint):
            nums.append(constraint.split('=')[1].strip())

    b_matrix = np.array([num for num in nums], dtype=float)
    print(b_matrix)

    # Prox passo: construir matrix A
    # <= vira 1
    # >= vira -1
    # ignoramos o =

