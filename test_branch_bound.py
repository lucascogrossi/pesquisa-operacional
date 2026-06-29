import itertools
import math
import sys

from main import parse_problem, solve_problem
from branch_bound import branch_and_bound

TOL = 1e-6


def caixa_superior(constraints, num_vars):
    hi = [None] * num_vars
    for j in range(num_vars):
        ej = [1.0 if i == j else 0.0 for i in range(num_vars)]
        status, x, z = solve_problem(constraints, ej, num_vars, is_max=True)
        if status != 'otimo':
            return None
        hi[j] = int(math.floor(z + TOL))
    return hi


def forca_bruta(constraints, obj_coefs, num_vars, is_max):
    hi = caixa_superior(constraints, num_vars)
    if hi is None:
        return None
    ranges = [range(0, h + 1) for h in hi]

    melhor = None
    for ponto in itertools.product(*ranges):
        ok = True
        for coefs, sinal, rhs in constraints:
            lhs = sum(coefs[j] * ponto[j] for j in range(num_vars))
            if sinal == '<=' and lhs > rhs + TOL:
                ok = False
                break
            if sinal == '>=' and lhs < rhs - TOL:
                ok = False
                break
            if sinal == '=' and abs(lhs - rhs) > TOL:
                ok = False
                break
        if not ok:
            continue
        z = sum(obj_coefs[j] * ponto[j] for j in range(num_vars))
        if melhor is None or (z > melhor if is_max else z < melhor):
            melhor = z
    return melhor


TESTES = [
    ("ex6.1", -7, "min z = -2*x1-1*x2\n1*x1+1*x2 <= 4\n1*x1 <= 3\n1*x2 <= 3.5\n"),
    ("ex6.2", 40, "max z = 5*x1+8*x2\n1*x1+1*x2 <= 6\n5*x1+9*x2 <= 45\n"),
    ("ex6.3", 23, "max z = 5*x1+4*x2\n1*x1+1*x2 <= 5\n10*x1+6*x2 <= 45\n"),
    ("ex6.4_arenales", -19, "min z = -5*x1-1*x2\n7*x1-5*x2 <= 13\n3*x1+2*x2 <= 17\n"),
    ("ex6.5_taha_ilim", "ILIM", "max z = 5*x1+4*x2\n3*x1+2*x2 >= 5\n2*x1+3*x2 >= 7\n"),
    ("ex6.6", None, "max z = 6*x1+8*x2\n30*x1+20*x2 <= 310\n5*x1+10*x2 <= 113\n"),
    ("ex6.8", None, "max z = 9*x1+5*x2\n4*x1+9*x2 <= 35\n1*x1 <= 6\n1*x1-3*x2 >= 1\n3*x1+2*x2 <= 19\n"),
    ("ex6.9", None, "max z = 3*x1+2*x2\n2*x1+5*x2 <= 9\n4*x1+2*x2 <= 9\n"),
    ("knap", None, "max z = 1*x1+1*x2\n5*x1+4*x2 <= 22\n"),
    ("infact", "INFACT", "max z = 1*x1\n1*x1 <= 0.5\n1*x1 >= 0.8\n"),
]


def roda():
    passou = 0
    for nome, esperado, texto in TESTES:
        prob = parse_problem(texto.splitlines())
        status, x, z = branch_and_bound(
            prob['constraints'], prob['obj_coefs'], prob['num_vars'], prob['is_max'])

        if esperado == "ILIM":
            ok = (status == 'ilimitado')
            obtido = status
        elif esperado == "INFACT":
            ok = (status == 'infactivel')
            obtido = status
        else:
            obtido = z if status == 'otimo' else status
            ok = (status == 'otimo')
            if ok and esperado is not None:
                ok = abs(z - esperado) <= 1e-6
            bruto = forca_bruta(prob['constraints'], prob['obj_coefs'],
                                prob['num_vars'], prob['is_max'])
            if ok and bruto is not None:
                ok = abs(z - bruto) <= 1e-6

        if status == 'otimo':
            for coefs, sinal, rhs in prob['constraints']:
                lhs = sum(coefs[j] * x[j] for j in range(prob['num_vars']))
                if sinal == '<=' and lhs > rhs + 1e-6:
                    ok = False
                if sinal == '>=' and lhs < rhs - 1e-6:
                    ok = False
                if sinal == '=' and abs(lhs - rhs) > 1e-6:
                    ok = False
            if any(abs(v - round(v)) > 1e-6 for v in x):
                ok = False

        passou += ok
        marca = "PASS" if ok else "FAIL"
        sol = f" x={x}" if status == 'otimo' else ""
        print(f"[{marca}] {nome:18} esperado={str(esperado):8} obtido={obtido}{sol}")

    print(f"\n{passou}/{len(TESTES)} testes passaram")
    return passou == len(TESTES)


if __name__ == "__main__":
    sys.exit(0 if roda() else 1)
