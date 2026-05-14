import numpy as np
import re

with open('data.txt', 'r') as f:

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

    # Se for max, multiplica a funcao objetivo por -1 (simplex minimiza)
    if is_max:
        cost_matrix = -cost_matrix


# ----------------------------------------------------------------------
# Fase 2 do metodo Simplex
# ----------------------------------------------------------------------

def calcula_lambda(B, c_B):
    # Resolve o sistema B^T * lambda = c_B
    # Programar dps no blas.py
    return np.linalg.solve(B.T, c_B)


def sorteia_particao_basica(A, b, max_tentativas=1000):
    m, n = A.shape
    indices = np.arange(n)

    for tentativa in range(max_tentativas):
        np.random.shuffle(indices)
        B_idx = sorted(indices[:m].tolist())
        N_idx = sorted(indices[m:].tolist())

        B = A[:, B_idx]

        if abs(np.linalg.det(B)) < 1e-10:
            continue

        try:
            x_B = np.linalg.solve(B, b)
        except np.linalg.LinAlgError:
            continue

        if np.all(x_B >= -1e-10):
            print(f"\nParticao basica factivel encontrada na tentativa {tentativa + 1}")
            return B_idx, N_idx

    raise RuntimeError("Nao foi possivel sortear uma particao basica factivel")


def fase2(A, b, c, B_idx, N_idx, max_iter=100):
    n = A.shape[1]
    B_idx = list(B_idx)
    N_idx = list(N_idx)

    for iteracao in range(1, max_iter + 1):
        print("\n" + "=" * 80)
        print(f"Iteracao {iteracao}")
        print("=" * 80)

        B = A[:, B_idx]
        N = A[:, N_idx]
        c_B = c[B_idx]
        c_N = c[N_idx]

        # Passo 1: calculo da solucao basica
        x_B = np.linalg.solve(B, b)
        f_x = c_B @ x_B
        print(f"Indices basicos (B):     {[i + 1 for i in B_idx]}")
        print(f"Indices nao-basicos (N): {[i + 1 for i in N_idx]}")
        print(f"x_B = {x_B}")
        print(f"f(x) = {f_x}")

        # Passo 2: calculo dos custos relativos
        # 2.1) vetor multiplicador simplex
        lam = calcula_lambda(B, c_B)
        print(f"lambda = {lam}")

        # 2.2) custos relativos
        c_hat_N = c_N - lam @ N
        print(f"custos relativos: {c_hat_N}")

        # 2.3) determinacao da variavel a entrar na base
        k = int(np.argmin(c_hat_N))
        c_hat_N_k = c_hat_N[k]

        # Passo 3: teste de otimalidade
        if c_hat_N_k >= -1e-10:
            print("\nSolucao otima encontrada!")
            x = np.zeros(n)
            x[B_idx] = x_B
            return x, f_x

        print(f"Entra na base: x{N_idx[k] + 1} (custo relativo = {c_hat_N_k})")

        # Passo 4: calculo da direcao simplex
        a_Nk = A[:, N_idx[k]]
        y = np.linalg.solve(B, a_Nk)
        print(f"y = {y}")

        # Passo 5: determinacao do passo e variavel a sair da base
        if np.all(y <= 0):
            print("Problema nao tem solucao otima finita (f(x) -> -inf)")
            return None, -np.inf

        razoes = np.full_like(y, np.inf, dtype=float)
        mask = y > 1e-10
        razoes[mask] = x_B[mask] / y[mask]
        l = int(np.argmin(razoes))
        epsilon = razoes[l]
        print(f"epsilon = {epsilon}, sai da base: x{B_idx[l] + 1}")

        # Passo 6: atualizacao da particao basica
        B_idx[l], N_idx[k] = N_idx[k], B_idx[l]

    print("Limite de iteracoes atingido")
    return None, None


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("# Fase 2 do Simplex")
    print("#" * 80)

    B_idx, N_idx = sorteia_particao_basica(a_matrix, b_matrix)
    x_otimo, f_otimo = fase2(a_matrix, b_matrix, cost_matrix, B_idx, N_idx)

    if x_otimo is not None:
        print("\n" + "#" * 80)
        print(f"x* = {x_otimo}")
        # Se o problema original era de max, inverte o sinal do otimo
        valor_original = -f_otimo if is_max else f_otimo
        print(f"f(x*) = {valor_original}")
        print("#" * 80)
