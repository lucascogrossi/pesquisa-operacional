import numpy as np
import re
with open('temp.txt', 'r') as f:
    # Salva todo o conteudo do arquivo em uma variavel
    data = f.readlines()
    print("="*100)
    print(data)
    print("="*100)
 
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

    # Extrai os coeficientes da funcao objetiva
    print(f"Funcao objetiva: {fn[3]}")
    fn_coefficients = np.array(re.findall(r'(-?\d+)\s*\*?\s*x\d+', fn[3]), dtype=float)
    print(f"Coeficientes da funcao objetiva: {fn_coefficients}")

    # Constroi a matriz custo
    cost_matrix = np.zeros(num_vars + num_more_or_equal + num_less_or_equal)
    cost_matrix[:len(fn_coefficients)] = fn_coefficients
    print(f"Matriz custo: {cost_matrix}")

    # Constroi a matriz b
    b_matrix = np.zeros(len(constraints))
    nums = []
    for constraint in constraints:
        # https://stackoverflow.com/questions/6696027/how-to-split-elements-of-a-list
        if '<=' in constraint:
            nums.append(constraint.split('<=')[1].strip()) 
        elif '>=' in constraint:
            nums.append(constraint.split('>=')[1].strip())
        elif '=' in constraint and not ('<=' in constraint or '>=' in constraint):
            nums.append(constraint.split('=')[1].strip())

    b_matrix = np.array([num for num in nums], dtype=float)
    print(f"Matriz b: {b_matrix}")

    # Prox passo: construir matriz A
    # <= vira 1
    # >= vira -1
    # ignoramos o =
    a_matrix = np.zeros((len(constraints), num_vars + num_more_or_equal + num_less_or_equal))
    print(f"Matriz A:\n{a_matrix}")
    print(f"Resricoes: {constraints}")

    # Primeiro colocamos os coeficientes
    for i, constraint in enumerate(constraints):
        constraints_coefs = re.findall(r'(-?\d+)\s*\*?\s*x\d+', constraint)
        
        for j, coef in enumerate(constraints_coefs):
            a_matrix[i, j] = float(coef)
    print(f"Matriz A completando:\n{a_matrix}")

    # Prox passo: completar com os 1 e -1



