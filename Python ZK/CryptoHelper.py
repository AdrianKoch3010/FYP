
p = 2**256 - 2**224 + 2**192 + 2**96 - 1
g = 3007057779649931580237598654612510797095951971612630025891176454468165002055
h = 20354936247998155748817459761265066334754915076915271771709029462851510023744


def Commit(m, r):
    return pow(g, m, p) * pow(h, r, p) % p

#TODO: Write unit tetsts for calc_coeffs
def calc_coeffs(n, i, l, A):
    coeffs = [0] * n
    coeffs[0] = 1
    for j in range(n):
        # i[j] == 1 && l[j] == 1 => x + aj
        # i[j] == 1 && l[j] == 0 => aj
        # i[j] == 0 && l[j] == 1 => -aj
        # i[j] == 0 && l[j] == 0 => x - aj
        if i >> j & 1 == 1:
            if l >> j & 1 == 1:
                # x + aj
                new_coeffs = []
                for k in range(n):
                    new_coeffs.append(coeffs[k] * A[j])
                    if k != 0:
                        new_coeffs[k] = coeffs[k-1] + new_coeffs[k]
                coeffs = new_coeffs
            else:
                # aj
                for k in range(n):
                    coeffs[k] *= A[j]
        else:
            if l >> j & 1 == 1:
                # -aj
                for k in range(n):
                    coeffs[k] *= -A[j]
            else:
                # x - aj
                new_coeffs = []
                for k in range(n):
                    new_coeffs.append(coeffs[k] * -A[j])
                    if k != 0:
                        new_coeffs[k] = coeffs[k-1] + new_coeffs[k]
                coeffs = new_coeffs
    return coeffs

# print([calc_coeffs(3, i, 0b101, [3, 2, 5]) for i in range(8)])