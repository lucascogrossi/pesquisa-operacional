import math

from main import build_standard, resolve, parse_problem, limpa

INT_TOL = 1e-6


class No:
    def __init__(self, id, bounds, rotulo, pai):
        self.id = id
        self.bounds = bounds
        self.rotulo = rotulo
        self.pai = pai
        self.filhos = []
        self.status = None
        self.x = None
        self.z = None
        self.var = None


def _bound_constraint(num_vars, j, sinal, rhs):
    coefs = [0.0] * num_vars
    coefs[j] = 1.0
    return coefs, sinal, rhs


def _solve_relaxacao(base_constraints, bounds, obj_coefs, num_vars, is_max):
    constraints = list(base_constraints) + [
        _bound_constraint(num_vars, j, sinal, rhs) for (j, sinal, rhs) in bounds
    ]
    A, b, num_cols = build_standard(constraints, num_vars)
    c = [0.0] * num_cols
    c[:num_vars] = obj_coefs
    if is_max:
        c = [-v for v in c]
    return resolve(A, b, c, num_vars)


def _primeira_fracionaria(x, num_vars):
    for j in range(num_vars):
        if abs(x[j] - round(x[j])) > INT_TOL:
            return j
    return None


def _descricao(no, melhor):
    cab = f"P{no.id}"
    if no.rotulo:
        cab += f" ({no.rotulo})"
    if no.status == 'inviavel':
        return cab + "  inviavel"
    if no.status == 'ilimitado':
        return cab + "  ilimitado"
    xs = "(" + ", ".join(str(limpa(v)) for v in no.x) + ")"
    base = f"{cab}  x={xs}  z={limpa(no.z)}"
    if no.status == 'ramificado':
        return base + f"  -> ramifica x{no.var + 1}"
    if no.status == 'inteiro':
        return base + "  INTEIRA" + ("  <== OTIMA" if no is melhor else "")
    if no.status == 'podado':
        return base + "  podado (limitante)"
    return base


def imprime_arvore(no, melhor, prefixo="", raiz=True, ultimo=True):
    if raiz:
        print(_descricao(no, melhor))
        novo = ""
    else:
        ramo = "└── " if ultimo else "├── "
        print(prefixo + ramo + _descricao(no, melhor))
        novo = prefixo + ("    " if ultimo else "│   ")
    for i, filho in enumerate(no.filhos):
        imprime_arvore(filho, melhor, novo, raiz=False, ultimo=(i == len(no.filhos) - 1))


def branch_and_bound(base_constraints, obj_coefs, num_vars, is_max, mostrar_arvore=False):
    melhor_f = math.inf
    melhor_x = None
    melhor_no = None
    relax_ilimitada = False

    raiz = No(0, [], None, None)
    contador = 1
    pilha = [raiz]

    while pilha:
        no = pilha.pop()
        status, x, f = _solve_relaxacao(
            base_constraints, no.bounds, obj_coefs, num_vars, is_max)

        if status == 'infactivel':
            no.status = 'inviavel'
            continue
        if status == 'ilimitado':
            no.status = 'ilimitado'
            relax_ilimitada = True
            continue

        no.x = x
        no.z = -f if is_max else f

        if f >= melhor_f - 1e-9:
            no.status = 'podado'
            continue

        j = _primeira_fracionaria(x, num_vars)
        if j is None:
            no.status = 'inteiro'
            melhor_f = f
            melhor_x = [int(round(x[i])) for i in range(num_vars)]
            melhor_no = no
            continue

        no.status = 'ramificado'
        no.var = j
        v = x[j]
        piso = math.floor(v + INT_TOL)

        filho_le = No(contador, no.bounds + [(j, '<=', float(piso))],
                      f"x{j + 1} <= {piso}", no)
        filho_ge = No(contador + 1, no.bounds + [(j, '>=', float(piso + 1))],
                      f"x{j + 1} >= {piso + 1}", no)
        contador += 2
        no.filhos = [filho_le, filho_ge]
        pilha.append(filho_le)
        pilha.append(filho_ge)

    if mostrar_arvore:
        print("Arvore Branch and Bound:")
        imprime_arvore(raiz, melhor_no)
        print()

    if melhor_x is None:
        return ('ilimitado', None, None) if relax_ilimitada else ('infactivel', None, None)

    z = -melhor_f if is_max else melhor_f
    return 'otimo', melhor_x, z


if __name__ == "__main__":
    with open('data.txt', 'r') as f:
        prob = parse_problem(f.readlines())

    status, x_otimo, z = branch_and_bound(
        prob['constraints'], prob['obj_coefs'], prob['num_vars'], prob['is_max'],
        mostrar_arvore=True)

    print(prob['fn'].strip(), " (x inteiro)")
    for restricao in prob['raw']:
        print(restricao.strip())
    print()

    if status == 'otimo':
        for i, xi in enumerate(x_otimo):
            print(f"x{i + 1} = {xi}")
        print(f"z = {limpa(z)}")
    elif status == 'ilimitado':
        print("Problema ilimitado")
    else:
        print("Problema infactivel")
