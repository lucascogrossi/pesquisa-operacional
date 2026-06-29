import re

from BLAS import dot, matvec, inverse, transpose, solve


def parse_coefs(expr, num_vars):
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


def parse_constraint(line, num_vars):
    if '<=' in line:
        sinal = '<='
    elif '>=' in line:
        sinal = '>='
    else:
        sinal = '='
    lhs, rhs = re.split(r'[<>]?=', line, maxsplit=1)
    return parse_coefs(lhs, num_vars), sinal, float(rhs.strip())


def parse_problem(linhas):
    linhas = [l.replace('−', '-').replace('–', '-') for l in linhas]
    fn = linhas[0]
    is_max = (fn.split()[0] == 'max')
    obj_expr = fn.split('=', 1)[1]

    raw = [c for c in linhas[1:] if c.strip()]
    todos_indices = re.findall(r'x(\d+)', ' '.join([fn] + raw))
    num_vars = max(int(i) for i in todos_indices)

    obj_coefs = parse_coefs(obj_expr, num_vars)
    constraints = [parse_constraint(c, num_vars) for c in raw]
    return {
        'fn': fn,
        'is_max': is_max,
        'obj_coefs': obj_coefs,
        'constraints': constraints,
        'raw': raw,
        'num_vars': num_vars,
    }


def build_standard(constraints, num_vars):
    m = len(constraints)
    num_extra = sum(1 for (_, s, _) in constraints if s in ('<=', '>='))
    num_cols = num_vars + num_extra

    A = [[0.0] * num_cols for _ in range(m)]
    b = [0.0] * m
    extra = num_vars
    for i, (coefs, sinal, rhs) in enumerate(constraints):
        A[i][:num_vars] = coefs
        if sinal == '<=':
            A[i][extra] = 1.0
            extra += 1
        elif sinal == '>=':
            A[i][extra] = -1.0
            extra += 1
        b[i] = rhs
    return A, b, num_cols


def solve_problem(constraints, obj_coefs, num_vars, is_max):
    A, b, num_cols = build_standard(constraints, num_vars)
    c = [0.0] * num_cols
    c[:num_vars] = obj_coefs
    if is_max:
        c = [-v for v in c]
    return resolve(A, b, c, num_vars)


def itera_simplex(A, b, c, B_idx, N_idx, max_iter=10000):
    B_idx = list(B_idx)
    N_idx = list(N_idx)
    m = len(A)

    for _ in range(max_iter):
        B = cols(A, B_idx)
        x_B = solve(B, b)

        c_B = [c[i] for i in B_idx]
        lam = solve(transpose(B), c_B)
        c_hat = [c[j] - dot(lam, col(A, j)) for j in N_idx]
        k = min(range(len(N_idx)), key=lambda t: c_hat[t])

        if c_hat[k] >= -1e-9:
            return 'otimo', B_idx, N_idx, x_B

        y = solve(B, col(A, N_idx[k]))

        positivos = [i for i in range(m) if y[i] > 1e-9]
        if not positivos:
            return 'ilimitado', B_idx, N_idx, x_B
        razao_min = min(x_B[i] / y[i] for i in positivos)
        l = min((i for i in positivos if x_B[i] / y[i] <= razao_min + 1e-9),
                key=lambda i: B_idx[i])

        B_idx[l], N_idx[k] = N_idx[k], B_idx[l]

    return 'limite', B_idx, N_idx, x_B


def resolve(A, b, c, num_vars):
    A = [list(linha) for linha in A]
    b = list(b)
    c = list(c)
    m = len(A)
    n = len(A[0])

    for i in range(m):
        if b[i] < 0:
            A[i] = [-v for v in A[i]]
            b[i] = -b[i]

    A1 = [A[i] + [1.0 if j == i else 0.0 for j in range(m)] for i in range(m)]
    art = list(range(n, n + m))
    c_fase1 = [0.0] * n + [1.0] * m

    status, B_idx, N_idx, x_B = itera_simplex(A1, b, c_fase1, art, list(range(n)))

    valor_artificial = dot([c_fase1[i] for i in B_idx], x_B)
    if valor_artificial > 1e-7:
        return 'infactivel', None, None

    for pos in range(m):
        if B_idx[pos] in art:
            Binv = inverse(cols(A1, B_idx))
            for jp, j in enumerate(N_idx):
                if j in art:
                    continue
                if abs(matvec(Binv, col(A1, j))[pos]) > 1e-7:
                    B_idx[pos], N_idx[jp] = N_idx[jp], B_idx[pos]
                    break

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
    with open('data.txt', 'r') as f:
        prob = parse_problem(f.readlines())

    status, x_otimo, f_otimo = solve_problem(
        prob['constraints'], prob['obj_coefs'], prob['num_vars'], prob['is_max'])

    print(prob['fn'].strip())
    for restricao in prob['raw']:
        print(restricao.strip())
    print()

    if status == 'otimo':
        valor_original = -f_otimo if prob['is_max'] else f_otimo
        for i, xi in enumerate(x_otimo):
            print(f"x{i + 1} = {limpa(xi)}")
        print(f"z = {limpa(valor_original)}")
    elif status == 'ilimitado':
        print("Problema ilimitado")
    else:
        print("Problema infactivel")
