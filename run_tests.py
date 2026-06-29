import subprocess
import re
import sys

PY = sys.executable 
TOL = 1e-2 

tests = [
    ("1_a", 11.6,    "max z = 1*x1+1*x2\n2*x1+1*x2 <= 18\n-1*x1+2*x2 <= 4\n3*x1-6*x2 <= 12\n"),
    ("1_b", 66,      "max z = 6*x1+2*x2\n3*x1+1*x2 <= 33\n1*x1+1*x2 <= 13\n"),
    ("1_c", 3,       "max z = 1*x1+1*x2\n2*x1+1*x2 <= 8\n1*x1+2*x2 <= 3\n"),
    ("1_d", 45,      "max z = 3*x1+1*x2\n2*x1+1*x2 <= 30\n1*x1+4*x2 <= 40\n"),
    ("1_e", 352.5,   "max z = 2*x1+5*x2\n3*x1+10*x2 <= 600\n1*x1+2*x2 <= 162\n"),
    ("1_f", 1.6667,  "min z = -1*x1+2*x2\n-2*x1+1*x2 <= 3\n3*x1+4*x2 <= 5\n1*x1-1*x2 <= 2\n"),
    ("1_g", 0.322581, "min z = -1*x1+2*x2\n1*x1+1*x2 >= 1\n-5*x1+2*x2 >= -10\n3*x1+5*x2 >= 15\n"),
    ("1_h", "ILIM",  "max z = 2*x1+2*x2\n-0.5*x1+1*x2 <= 2\n1*x1-1*x2 >= -1\n"),
    ("1_i", 11.6,    "max z = 1*x1+1*x2\n2*x1+1*x2 <= 18\n-1*x1+2*x2 <= 4\n3*x1-6*x2 >= -12\n"),
    ("1_j", 0.0,     "min z = 4*x1-12*x2\n2*x1+1*x2 >= 6\n1*x1+3*x2 <= 8\n1*x1 >= 4\n"),
    ("1_k", 5,       "min z = -1*x1-1*x2+0*x3\n1*x1+1*x3 >= 1\n1*x1-3*x2-1*x3 >= 1\n1*x1-1*x2+5*x3 >= 5\n1*x1+1*x2+1*x3 <= 5\n"),
    ("1_l", 30,      "max z = 3*x1+3*x2+0*x3\n1*x1+3*x3 <= 5\n1*x2 <= 5\n3*x1+2*x3 >= 6\n1*x1+1*x2 <= 10\n"),
    ("1_m", "INFACT", "max z = 4*x1+3*x2\n1*x1+3*x2 <= 7\n2*x1+2*x2 = 8\n1*x1+1*x2 <= -3\n1*x2 <= 2\n"),
    ("2_a", 45,      "max z = 3*x1+1*x2\n2*x1+1*x2 <= 30\n1*x1+4*x2 <= 40\n"),
    ("2_b", 352.5,   "max z = 2*x1+5*x2\n3*x1+10*x2 <= 600\n1*x1+2*x2 <= 162\n"),
    ("2_c", 1.6666,  "min z = -1*x1+2*x2\n-2*x1+1*x2 <= 3\n3*x1+4*x2 <= 5\n1*x1-1*x2 <= 2\n"),
    ("2_d", 11.6666, "max z = 1*x1+1*x2\n2*x1+1*x2 <= 18\n-1*x1+2*x2 <= 4\n3*x1-6*x2 >= -12\n"),
    ("2_e", 30,      "max z = 3*x1+3*x2+0*x3\n1*x1+3*x3 <= 5\n1*x2 <= 5\n3*x1+2*x3 >= 6\n1*x1+1*x2 <= 10\n"),
    ("2_f", "INFACT", "max z = 4*x1+3*x2\n1*x1+3*x2 <= 7\n2*x1+2*x2 = 8\n1*x1+1*x2 <= -3\n1*x2 <= 2\n"),
    ("2_g", "INFACT", "max z = 4*x1+8*x2\n3*x1+2*x2 = 18\n1*x1+1*x2 <= 5\n1*x1 <= 4\n"),
    ("extra1", 248.3333, "min z = -2.5*x1-5.7*x2-1*x3-2*x4\n1*x2+1*x3 <= 18\n-1.5*x1+2.5*x2 <= 4\n3*x1-6*x2+1*x4 <= 12.7\n"),
    ("extra2", 15,   "max z = 3*x1+3*x2+13*x3\n-3*x1+6*x2+7*x3 <= 8\n6*x1-3*x2+7*x3 <= 8\n1*x1 <= 2\n1*x3 >= 1\n"),
    ("extra3", 99.2857, "max z = 4*x1+5*x2+9*x3+11*x4\n1*x1+1*x2+1*x3+1*x4 <= 15\n7*x1+5*x2+3*x3+2*x4 <= 120\n3*x1+5*x2+10*x3+15*x4 <= 100\n"),
    ("extra4", 12.3684, "min z = -5*x1-3*x2\n3*x1+5*x2 <= 15\n5*x1+2*x2 <= 10\n"),
]


def roda(content):
    with open('data.txt', 'w') as f:
        f.write(content)
    r = subprocess.run([PY, 'main.py'], capture_output=True, text=True)
    out = r.stdout + r.stderr
    m = re.search(r'^z = (.*)$', out, re.M)
    if m:
        return ('VAL', float(m.group(1).strip()))
    if 'ilimitado' in out:
        return ('ILIM', None)
    if 'infactivel' in out:
        return ('INFACT', None)
    return ('ERRO', out)


def confere(esperado, status, valor):
    if isinstance(esperado, str):
        return status == esperado
    return status == 'VAL' and abs(abs(valor) - abs(esperado)) <= TOL + TOL * abs(esperado)


try:
    with open('data.txt', 'r') as f:
        data_original = f.read()
except FileNotFoundError:
    data_original = None

passou = 0
try:
    for name, esperado, content in tests:
        status, valor = roda(content)
        ok = confere(esperado, status, valor)
        passou += ok
        obtido = valor if status == 'VAL' else status
        esp_txt = esperado if isinstance(esperado, str) else f"{esperado}"
        marca = "PASS" if ok else "FAIL"
        print(f"[{marca}] {name:7} esperado={esp_txt:9} obtido={obtido}")
finally:
    if data_original is not None:
        with open('data.txt', 'w') as f:
            f.write(data_original)

print(f"\n{passou}/{len(tests)} testes passaram")
sys.exit(0 if passou == len(tests) else 1)
