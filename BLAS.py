EPS = 1e-12


def zeros(linhas, colunas):
    return [[0.0] * colunas for _ in range(linhas)]


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def transpose(A):
    return [list(coluna) for coluna in zip(*A)]


def matmul(A, B):
    m, n = len(A), len(A[0])
    n2, p = len(B), len(B[0])
    if n != n2:
        raise ValueError("dimensoes incompativeis para multiplicacao")
    C = zeros(m, p)
    for i in range(m):
        for k in range(p):
            soma = 0.0
            for j in range(n):
                soma += A[i][j] * B[j][k]
            C[i][k] = soma
    return C


def matvec(A, x):
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def determinant(A):
    n = len(A)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    det = 0.0
    for j in range(n):
        menor = [[A[i][c] for c in range(n) if c != j] for i in range(1, n)]
        det += ((-1) ** j) * A[0][j] * determinant(menor)
    return det


def solve(A, b):
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < EPS:
            raise ValueError("matriz singular")
        M[col], M[piv] = M[piv], M[col]
        for r in range(n):
            if r != col:
                fator = M[r][col] / M[col][col]
                if fator != 0.0:
                    for c in range(col, n + 1):
                        M[r][c] -= fator * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def inverse(A):
    n = len(A)
    M = [list(A[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < EPS:
            raise ValueError("matriz singular - sem inversa")
        M[col], M[piv] = M[piv], M[col]
        pivo = M[col][col]
        for c in range(2 * n):
            M[col][c] /= pivo
        for r in range(n):
            if r != col:
                fator = M[r][col]
                for c in range(2 * n):
                    M[r][c] -= fator * M[col][c]
    return [linha[n:] for linha in M]
