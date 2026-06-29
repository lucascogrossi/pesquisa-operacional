import re

from BLAS import dot, matvec, inverse, transpose, solve


def parse_coefs(expr, num_vars):
    # coeficientes implicitos: 'x1' -> 1, '-x2' -> -1
    coefs = [0.0] * num_vars
    for raw, idx in re.findall(r'([+-]?\s*\d*\.?\d*)\s*\*?\s*x(\d+)', expr):
        s = raw.replace(' ', '')
        if s in ('', '+'):
            val = 1.0
        elif s == '-':
            val = -1.0
        else:
            val = float(s)
        coefs[int(idx) - 1] = val
    return coefs


def col(A, j):
    return [linha[j] for linha in A]


def cols(A, idxs):
    return [[linha[j] for j in idxs] for linha in A]


with open('data.txt', 'r') as f:
    data = f.readlines()
    data = [line.replace('−', '-').replace('–', '-') for line in data]

    fn = data[0]
    is_max = (fn.split()[0] == 'max')
    obj_expr = fn.split('=', 1)[1]

    constraints = [c for c in data[1:] if c.strip()]
    num_ineqs = len(constraints)

    # maior indice de variavel em toda a entrada
    todos_indices = re.findall(r'x(\d+)', data[0] + ''.join(constraints))
    num_vars = max(int(i) for i in todos_indices)

    num_more_or_equal = len([line for line in constraints if ">=" in line])
    num_less_or_equal = len([line for line in constraints if "<=" in line])

    fn_coefficients = parse_coefs(obj_expr, num_vars)

    # custo: variaveis originais + excesso + folga
    num_cols = num_vars + num_more_or_equal + num_less_or_equal
    cost_matrix = [0.0] * num_cols
    cost_matrix[:num_vars] = fn_coefficients

    nums = []
    for constraint in constraints:
        if '<=' in constraint:
            nums.append(constraint.split('<=')[1].strip())
        elif '>=' in constraint:
            nums.append(constraint.split('>=')[1].strip())
        elif '=' in constraint:
            nums.append(constraint.split('=')[1].strip())

    b_matrix = [float(num) for num in nums]

    # matriz A: >= recebe excesso (-1), <= recebe folga (+1), = nao recebe nada
    a_matrix = [[0.0] * num_cols for _ in range(len(constraints))]

    for i, constraint in enumerate(constraints):
        lhs = re.split(r'[<>]?=', constraint)[0]
        a_matrix[i][:num_vars] = parse_coefs(lhs, num_vars)

    more_or_equal_idx = num_vars
    less_or_equal_idx = num_vars + num_more_or_equal
    for i, constraint in enumerate(constraints):
        if '>=' in constraint:
            a_matrix[i][more_or_equal_idx] = -1.0
            more_or_equal_idx += 1
        elif '<=' in constraint:
            a_matrix[i][less_or_equal_idx] = 1.0
            less_or_equal_idx += 1

    # simplex minimiza; se for max, troca o sinal do objetivo
    if is_max:
        cost_matrix = [-c for c in cost_matrix]


# ----------------------------------------------------------------------
# Metodo Simplex (Fase I + Fase II)
# ----------------------------------------------------------------------

def itera_simplex(A, b, c, B_idx, N_idx, max_iter=10000):
    # iteracao simplex a partir da particao basica A=[B N]
    B_idx = list(B_idx)
    N_idx = list(N_idx)
    m = len(A)

    for _ in range(max_iter):
        # Passo 1: calculo da solucao basica  ->  resolve B x_B = b  (x_N = 0)
        B = cols(A, B_idx)
        x_B = solve(B, b)

        # Passo 2: custos relativos
        c_B = [c[i] for i in B_idx]
        lam = solve(transpose(B), c_B)                 # B^T lambda = c_B
        c_hat = [c[j] - dot(lam, col(A, j)) for j in N_idx]   # c_Nj - lambda^T a_Nj
        # variavel a entrar: regra de Dantzig (menor custo relativo)
        k = min(range(len(N_idx)), key=lambda t: c_hat[t])

        # Passo 3: teste de otimalidade  ->  se c_hat_Nk >= 0, e otima
        if c_hat[k] >= -1e-9:
            return 'otimo', B_idx, N_idx, x_B

        # Passo 4: direcao simplex  ->  resolve B y = a_Nk
        y = solve(B, col(A, N_idx[k]))

        # Passo 5: passo e variavel a sair (razao minima)
        positivos = [i for i in range(m) if y[i] > 1e-9]
        if not positivos:                              # y <= 0  ->  f(x) -> -inf
            return 'ilimitado', B_idx, N_idx, x_B
        razao_min = min(x_B[i] / y[i] for i in positivos)
        # entre empates, menor indice basico (regra de Bland p/ evitar ciclagem)
        l = min((i for i in positivos if x_B[i] / y[i] <= razao_min + 1e-9),
                key=lambda i: B_idx[i])

        # Passo 6: atualizacao - troca a l-esima coluna de B pela k-esima de N
        B_idx[l], N_idx[k] = N_idx[k], B_idx[l]

    return 'limite', B_idx, N_idx, x_B


def resolve(A, b, c, num_vars):
    # min c^T x, s.a Ax = b, x >= 0 pelo metodo das duas fases
    A = [list(linha) for linha in A]
    b = list(b)
    c = list(c)
    m = len(A)
    n = len(A[0])

    # garante b >= 0
    for i in range(m):
        if b[i] < 0:
            A[i] = [-v for v in A[i]]
            b[i] = -b[i]

    # Fase I: uma variavel artificial por restricao (base = identidade)
    A1 = [A[i] + [1.0 if j == i else 0.0 for j in range(m)] for i in range(m)]
    art = list(range(n, n + m))
    c_fase1 = [0.0] * n + [1.0] * m

    status, B_idx, N_idx, x_B = itera_simplex(A1, b, c_fase1, art, list(range(n)))

    valor_artificial = dot([c_fase1[i] for i in B_idx], x_B)
    if valor_artificial > 1e-7:
        return 'infactivel', None, None

    # tira artificiais que sobraram na base (nivel zero) por pivoteamento
    for pos in range(m):
        if B_idx[pos] in art:
            Binv = inverse(cols(A1, B_idx))
            for jp, j in enumerate(N_idx):
                if j in art:
                    continue
                if abs(matvec(Binv, col(A1, j))[pos]) > 1e-7:
                    B_idx[pos], N_idx[jp] = N_idx[jp], B_idx[pos]
                    break

    # Fase II: custo original, artificiais proibidas de reentrar na base
    c_fase2 = list(c) + [0.0] * m
    N_idx = [j for j in N_idx if j not in art]

    status, B_idx, N_idx, x_B = itera_simplex(A1, b, c_fase2, B_idx, N_idx)

    if status == 'ilimitado':
        return 'ilimitado', None, None

    x = [0.0] * (n + m)
    for i, bi in enumerate(B_idx):
        x[bi] = x_B[i]
    f = dot(c_fase2, x)
    return 'otimo', x[:num_vars], f


def limpa(v):
    v = round(v, 6)
    return 0.0 if v == 0 else v


if __name__ == "__main__":
    status, x_otimo, f_otimo = resolve(a_matrix, b_matrix, cost_matrix, num_vars)

    print(fn.strip())
    for restricao in constraints:
        print(restricao.strip())
    print()

    if status == 'otimo':
        valor_original = -f_otimo if is_max else f_otimo
        for i, xi in enumerate(x_otimo):
            print(f"x{i + 1} = {limpa(xi)}")
        print(f"z = {limpa(valor_original)}")
    elif status == 'ilimitado':
        print("Problema ilimitado")
    else:
        print("Problema infactivel")
