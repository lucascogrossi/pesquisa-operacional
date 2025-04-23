import numpy as np
import re

with open('temp.txt', 'r') as f:

    # Salva todo o conteudo do arquivo em uma variavel
    data = f.readlines()
    print("="*80)
    print(data)
    print("="*80)
 
    # Funcao objetiva
    fn = data[0].split()
    is_max = (fn[0] == 'max')
    #print(f"is max? {is_max}")
    
    # Quantidade de variaveis (x1, x2, ..., xn)
    num_vars = len(re.findall(r'x\d+', fn[3])) 

    # Quantidade de restricoes
    constraints = data[1:]
    num_ineqs = len(constraints)
    #print(f"Numero de restricoes: {num_ineqs}")

    # Quantidade de >= e <=
    num_more_or_equal = len([line for line in constraints if ">=" in line])
    num_less_or_equal = len([line for line in constraints if "<=" in line])
    #print(f"Numero de maior ou igual: {num_more_or_equal}")
    #print(f"Numero de menor ou igual: {num_less_or_equal}")

    # Extrai os coeficientes da funcao objetiva
    print(f"Funcao objetiva: {fn[3]}")
    # agr pega decimais
    fn_coefficients = np.array(re.findall(r'(-?\d+\.?\d*)\s*\*?\s*x\d+', fn[3]), dtype=float)
    #print(f"Coeficientes da funcao objetiva: {fn_coefficients}")

    # Constroi a matriz custo
    cost_matrix = np.zeros(num_vars + num_more_or_equal + num_less_or_equal)
    cost_matrix[:len(fn_coefficients)] = fn_coefficients
    print(f"Matriz custo: {cost_matrix}")

    # Constroi a matriz b 
    b_matrix = np.zeros(len(constraints))
    nums = []

    # https://stackoverflow.com/questions/6696027/how-to-split-elements-of-a-list
    for constraint in constraints:
        if '<=' in constraint:
            nums.append(constraint.split('<=')[1].strip()) 
        elif '>=' in constraint:
            nums.append(constraint.split('>=')[1].strip())
        elif '=' in constraint and not ('<=' in constraint or '>=' in constraint):
            nums.append(constraint.split('=')[1].strip())

    b_matrix = np.array([num for num in nums], dtype=float)
    print(f"Matriz b: {b_matrix}")

    # Prox passo: construir matriz A
    # >= vira -1
    # <= vira 1
    # ignoramos o =
    a_matrix = np.zeros((len(constraints), num_vars + num_more_or_equal + num_less_or_equal))
    #print(f"Matriz A:\n{a_matrix}")
    #print(f"Resricoes: {constraints}")

    # Primeiro colocamos os coeficientes
    #print("vai loopar aqui: ")
    #print(list(enumerate(constraints)))
    for i, constraint in enumerate(constraints):
        # Inicializa um array de zeros para todas as variáveis
        coefficients = np.zeros(num_vars)
        #print(coefficients)
        
        # Encontra todos os termos na restrição com seus índices
        terms = re.findall(r'(-?\d+\.?\d*)\s*\*?\s*x(\d+)', constraint)
        #print(terms)
        
        for coef, var_idx in terms:
            # Ajudat pois começamos com x1 porem array começa em 0
            var_idx = int(var_idx) - 1
            coefficients[var_idx] = float(coef)
        
        # Atribui os coeficientes à matriz A
        a_matrix[i, :num_vars] = coefficients
    
    #print(f"Matriz A completando com os coeficientes:\n{a_matrix}")

    # Prox passo: completar com os 1 e -1
    more_or_equal_idx = num_vars
    less_or_equal_idx = num_vars + num_more_or_equal

    for i, constraint in enumerate(constraints):
        if '>=' in constraint:
            a_matrix[i, more_or_equal_idx] = -1
            more_or_equal_idx += 1
        elif '<=' in constraint:
            a_matrix[i, less_or_equal_idx] = 1
            less_or_equal_idx += 1
    print(f"Matriz A:\n{a_matrix}")



