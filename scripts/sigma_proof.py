# from Crypto.Random import random
from brownie import convert
from Crypto.PublicKey import ECC
from scripts import crypto_helper as ch
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
    
    def to_tuple(self):
        # F, Za, Zb, zd must be converted to big numbers
        F_tup = []
        Za_tup = []
        Zb_tup = []
        for num in self.response.F:
            F_tup.append(ch.BigNum(num).to_tuple())
        for num in self.response.Za:
            Za_tup.append(ch.BigNum(num).to_tuple())
        for num in self.response.Zb:
            Zb_tup.append(ch.BigNum(num).to_tuple())

        # Assemble the final tuple
        tup = []
        tup.append(self.commitment.Cl)
        tup.append(self.commitment.Ca)
        tup.append(self.commitment.Cb)
        tup.append(self.commitment.Cd)
        tup.append(F_tup)
        tup.append(Za_tup)
        tup.append(Zb_tup)
        tup.append(ch.BigNum(self.response.zd).to_tuple())
        return tup

# hash all the given information together to create a random oracle
# The hash must inlcude some public information
# The hash must be deterministic
# The message is a byte string
def hash_all(serial_number: int, message: str, commitments: list, proof: SigmaProof.Commitment) -> int:
    # hash the serial number
    result = SHA256.new(convert.to_bytes(serial_number)).digest()

    # hash the message
    result = SHA256.new(result + message).digest()

    # concatenate all the points
    points = [ch.g, ch.h]
    points += commitments
    points += proof.Cl
    points += proof.Ca
    points += proof.Cb
    points += proof.Cd

    # hash all the points
    for point in points:
        result = SHA256.new(result + convert.to_bytes(point)).digest()

    return int.from_bytes(result, byteorder='big')



# l is the index of the commitment (to 0) to generate the proof for
# r_0_commitment is the secret blinding factor used in c_l = commit(S, r)
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
        r = random.randint(2, ch.ffc_p-2) if generate_new else (j + 87654) * 34567121313212339
        a = random.randint(2, ch.ffc_p-2) if generate_new else (j + 4344) * 354315123132132999
        s = random.randint(2, ch.ffc_p-2) if generate_new else (j + 234) * 35448548945132299
        t = random.randint(2, ch.ffc_p-2) if generate_new else (j + 4345) * 34568484231231329
        _p = random.randint(2, ch.ffc_p-2) if generate_new else (j + 534) * 97373745132123132
        R.append(r)
        A.append(a)
        S.append(s)
        T.append(t)
        P.append(_p)

        l_j = l >> j & 1
        print('l_{j}:'.format(j = j), l_j)
        Cl.append(ch.commit(l_j, r)) # commit to the jth bit of l
        Ca.append(ch.commit(a, s))
        Cb.append(ch.commit(l_j*a, t))


    # The coefficients depend on the values of A
    coeffs = [ch.calc_coeffs(n, i, l, A) for i in range(N)]

    # Calculate Cd values
    for j in range(n):
        cd = 1
        for i in range(N):
            cd = cd * pow(commitments[i], coeffs[i][j], ch.ffc_p) % ch.ffc_p
        cd = cd * ch.commit(0, P[j]) % ch.ffc_p
        Cd.append(cd)

    # Generate x as a random oracle
    x = hash_all(serial_number, b'Adrian', commitments, SigmaProof.Commitment(Cl, Ca, Cb, Cd))
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

def verify_proof(serial_number: int, commitments: list, proof: SigmaProof) -> Tuple[bool, str]:

    N = len(commitments)
    n = math.ceil(math.log(N, 2))
    assert N == 2**n, "N must be a power of 2"

    # Compute the challenge
    challenge = hash_all(serial_number, b'Adrian', commitments, proof.commitment)

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
        left = pow(Cl[j], x, ch.ffc_p) * Ca[j] % ch.ffc_p
        right = ch.commit(F[j], Za[j])
        print('Check 1.{j}: {true}'.format(j=j, true=left == right))
        check1 = check1 and (left == right)

    check2 = True
    for j in range(n):
        left = pow(Cl[j], x-F[j]) * Cb[j] % ch.ffc_p
        right = ch.ECC_commit(0, Zb[j])
        print('Check 2.{j}: {true}'.format(j=j, true=left == right))
        check2 = check2 and (left == right)

    print('Checking commitment to 0')
    left_product = 1
    for i in range(N):
        # Calculate the product of f_j,i_j
        product = 1
        for j in range(n):
            i_j = (i >> j) & 1
            if i_j == 1:
                product *= F[j]
            else:
                product *= x - F[j]
        left_product *= pow(commitments[i], product, ch.ffc_p) % ch.ffc_p

    # Calculate the sum of the other commitments
    right_product = 1
    for k in range(n):
        right_product *= pow(Cd[k], -pow(x, k)) % ch.ffc_p


    left = left_product * right_product % ch.ffc_p
    right = ch.commit(0, zd)
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
