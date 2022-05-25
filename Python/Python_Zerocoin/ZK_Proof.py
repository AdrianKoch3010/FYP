# from Crypto.Random import random
from HelperFunctions import *
from Crypto.Hash import SHA256
from Crypto.Random import random
import math
from typing import Tuple


class SigmaProof:
    def __init__(self, commitment, challenge: int, response):
        self.commitment = commitment
        self.challenge = challenge
        self.response = response
    
    class Commitment:
        def __init__(self, Cl: list, Ca: list, Cb: list, Cd: list):
            self.Cl = Cl
            self.Ca = Ca
            self.Cb = Cb
            self.Cd = Cd

    class Response:
        def __init__(self, F: list, Za: list, Zb: list, zd: int):
            self.F = F
            self.Za = Za
            self.Zb = Zb
            self.zd = zd


# hash all the given information together to create a random oracle
# The hash must inlcude some public information
# The hash must be deterministic
def hash_all(M: str, S: int, C: list, a: SigmaProof.Commitment) -> int:
    # hash the ECC points used in the commitment
    h = SHA256.new(G.x.to_bytes())
    h.update(G.y.to_bytes())
    h.update(H.x.to_bytes())
    h.update(H.y.to_bytes())

    # hash the transaction string
    h.update(bytes(M, 'utf-8'))
    # hash the coin serial number
    h.update(str(S).encode())

    # hash the coin commitments
    for comm in C:
        h.update(comm.x.to_bytes())
        h.update(comm.y.to_bytes())

    # hash step one of the proof
    assert len(a.Cl) == len(a.Ca) and len(a.Cl) == len(a.Cb) and len(a.Cl) == len(a.Cd)
    for i in range(len(a.Cl)):
        h.update(str(a.Cl[i]).encode())
        h.update(str(a.Ca[i]).encode())
        h.update(str(a.Cb[i]).encode())
        h.update(str(a.Cd[i]).encode())

    return int.from_bytes(h.digest(), byteorder='big')


# C is the list of commitments
# l is the index of the commitment to generate the proof for
# r is the secret blinding factor used in c_l = commit(S, r)
def generate_proof(commitments: list, serial_number: int, l: int, r_0_commitment: int) -> SigmaProof:
    generate_new = True

    N = len(commitments)
    n = math.ceil(math.log(N, 2))
    assert N == 2**n, "N must be a power of 2"
    

    R = []
    A = []
    S = []
    T = []
    P = []
    Cl = []
    Ca = []
    Cb = []
    Cd = []

    for j in range(n):
        r = random.randint(2, p-2) if generate_new else (j + 87654) * 34567
        a = random.randint(2, p-2) if generate_new else (j + 4344) * 3543
        s = random.randint(2, p-2) if generate_new else (j + 234) * 354
        t = random.randint(2, p-2) if generate_new else (j + 4345) * 3456
        _p = random.randint(2, p-2) if generate_new else (j + 534) * 97373
        R.append(r)
        A.append(a)
        S.append(s)
        T.append(t)
        P.append(_p)

        l_j = l >> j & 1
        print('l_{j}:'.format(j = j), l_j)
        Cl.append(ECC_commit(l_j, r)) # commit to the jth bit of l
        Ca.append(ECC_commit(a, s))
        Cb.append(ECC_commit(l_j*a, t))


    # The coefficients depend on the values of A
    coeffs = [calc_coeffs(n, i, l, A) for i in range(N)]

    # Calculate Cd values
    for j in range(n):
        cd = G.point_at_infinity()
        for i in range(N):
            cd += ECC_mul(coeffs[i][j], commitments[i])
        cd += ECC_commit(0, P[j])
        Cd.append(cd)

    # Generate x as a random oracle
    x = hash_all('Adrian', serial_number, commitments, SigmaProof.Commitment(Cl, Ca, Cb, Cd))
    print('x:', x)


    F = []
    Za = []
    Zb = []
    for j in range(n):
        l_j = l >> j & 1
        f = l_j * x + A[j]
        za = R[j] * x + S[j]
        zb = R[j] * (x-f) + T[j]
        F.append(f)
        Za.append(za)
        Zb.append(zb)

    #r = the r used in the commitment to c_l
    zd = r_0_commitment * pow(x, n) - sum([P[k] * pow(x, k) for k in range(n)])

    # Create the sigma proof
    sigma_response = SigmaProof.Response(F, Za, Zb, zd)
    sigma_proof = SigmaProof(SigmaProof.Commitment(Cl, Ca, Cb, Cd), x, sigma_response)
    return sigma_proof

def verify_proof(S: int, commitments: list, proof: SigmaProof) -> Tuple[bool, str]:

    N = len(commitments)
    n = math.ceil(math.log(N, 2))
    assert N == 2**n, "N must be a power of 2"

    # Compute the challenge
    challenge = hash_all('Adrian', S, commitments, proof.commitment)

    # Check that the challenge is correct
    # This is not stricly necessary, but it helps to prevent unnecessary computation
    if challenge != proof.challenge:
        return False, "Challenge is incorrect"

    print('Verifying proof...')
    x = proof.challenge
    Cl = proof.commitment.Cl
    Ca = proof.commitment.Ca
    Cb = proof.commitment.Cb
    Cd = proof.commitment.Cd
    F = proof.response.F
    Za = proof.response.Za
    Zb = proof.response.Zb
    zd = proof.response.zd

    print('Checking commitments to l')
    check1 = True
    for j in range(n):
        # left = pow(Cl[j], x, p) * Ca[j] % p
        left = ECC_mul(x, Cl[j]) + Ca[j]
        right = ECC_commit(F[j], Za[j])
        print('Check 1.{j}: {true}'.format(j=j, true=left == right))
        check1 = check1 and (left == right)

    check2 = True
    for j in range(n):
        # left = pow(Cl[j], x-F[j], p) * Cb[j] % p
        left = ECC_mul(x-F[j], Cl[j]) + Cb[j]
        right = ECC_commit(0, Zb[j])
        print('Check 2.{j}: {true}'.format(j=j, true=left == right))
        check2 = check2 and (left == right)

    print('Checking commitment to 0')
    outer_sum = G.point_at_infinity()
    for i in range(N):
        # Calculate the product of f_j,i_j
        product = 1
        for j in range(n):
            i_j = i >> j & 1
            if i_j == 1:
                product *= F[j]
            else:
                product *= x - F[j]
        outer_sum += ECC_mul(product, commitments[i])
    left_sum = outer_sum

    # Calculate the sum of the other commitments
    right_sum = G.point_at_infinity()
    for k in range(n):
        right_sum += ECC_mul(-pow(x, k), Cd[k])


    print('Worst case number of bits required: ', math.ceil(math.log(pow(x, n-1), 2)))

    left = left_sum + right_sum
    right = ECC_commit(0, zd)
    print('Check 3: {true}'.format(true=left == right))
    check3 = left == right

    error_string = ""
    if not check1:
        error_string += "Commitment to l is incorrect\n"
    if not check2:
        error_string += "Commitment to b is incorrect\n"
    if not check3:
        error_string += "Commitment to 0 is incorrect\n"

    if check1 and check2 and check3:
        return True, "Proof is valid"
    else:
        return False, error_string


# # main test program
# if __name__ == "__main__":
#     generate_new = True

#     # Create a list of commitments, one of which is a commitment to 0
#     commitments = []
#     l = 5
#     n = 3
#     N = 2**n
#     r_0_commitment = 0
#     assert l < N, "l must be less than N"
#     assert N == 2**math.ceil(math.log(N, 2)), "N must be a power of 2"

#     for i in range(N):
#         if i == l:
#             m = 0
#         else:
#             m = random.randint(2, p-2) if generate_new else (i + 234) * 5672
#         r = random.randint(2, p-2) if generate_new else (i + 9876) * 987654321
#         r_0_commitment = r if i == l else r_0_commitment
#         commitments.append(ECC_commit(m, r))

#     # Create a proof
#     proof = generate_proof(commitments, 45, l, r_0_commitment)

#     # Verify the proof
#     proof_valid, msg = verify_proof(45, commitments, proof)
#     print("The proof is valid:", proof_valid)
#     print("Message:", msg)