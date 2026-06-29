import math

from main import build_standard, resolve, parse_problem, limpa

INT_TOL = 1e-6


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


def branch_and_bound(base_constraints, obj_coefs, num_vars, is_max, verbose=False):
    melhor_f = math.inf
    melhor_x = None
    relax_ilimitada = False

    pilha = [[]]
    no_id = 0

    while pilha:
        bounds = pilha.pop()
        status, x, f = _solve_relaxacao(
            base_constraints, bounds, obj_coefs, num_vars, is_max)

        if verbose:
            z_no = (-f if is_max else f) if status == 'otimo' else None
            print(f"  no {no_id:3d}  bounds={bounds}  status={status}"
                  + (f"  z={limpa(z_no)} x={[limpa(v) for v in x]}"
                     if status == 'otimo' else ""))
        no_id += 1

        if status == 'infactivel':
            continue
        if status == 'ilimitado':
            relax_ilimitada = True
            continue

        if f >= melhor_f - 1e-9:
            continue

        j = _primeira_fracionaria(x, num_vars)
        if j is None:
            melhor_f = f
            melhor_x = [int(round(x[i])) for i in range(num_vars)]
            continue

        v = x[j]
        piso = math.floor(v + INT_TOL)
        pilha.append(bounds + [(j, '<=', float(piso))])
        pilha.append(bounds + [(j, '>=', float(piso + 1))])

    if melhor_x is None:
        return ('ilimitado', None, None) if relax_ilimitada else ('infactivel', None, None)

    z = -melhor_f if is_max else melhor_f
    return 'otimo', melhor_x, z


if __name__ == "__main__":
    with open('data.txt', 'r') as f:
        prob = parse_problem(f.readlines())

    status, x_otimo, z = branch_and_bound(
        prob['constraints'], prob['obj_coefs'], prob['num_vars'], prob['is_max'],
        verbose=True)

    print()
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
