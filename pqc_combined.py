import os
import hashlib
import struct
from kyber_py.kyber import Kyber768
from sphincs import SphincsPlus
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class KyberKEM:
    def __init__(self):
        self.scheme = Kyber768
        self.security_level = 3
        self.pk_size = 1184
        self.sk_size = 2400
        self.ct_size = 1088

    def keygen(self):
        pk, sk = self.scheme.keygen()
        return pk, sk

    def encapsulate(self, pk):
        ciphertext, shared_secret = self.scheme.enc(pk)
        return ciphertext, shared_secret

    def decapsulate(self, sk, ciphertext):
        shared_secret = self.scheme.dec(sk, ciphertext)
        return shared_secret


class SphincsSigner:
    VARIANTS = {
        'fast': 'sphincs-shake-256f',
        'small': 'sphincs-shake-256s',
    }

    def __init__(self, variant='small'):
        self.scheme = SphincsPlus(self.VARIANTS[variant])

    def keygen(self):
        pk, sk = self.scheme.keygen()
        return pk, sk

    def sign(self, sk, message: bytes) -> bytes:
        if isinstance(message, str):
            message = message.encode('utf-8')
        return self.scheme.sign(message, sk)

    def verify(self, pk, message: bytes, sig: bytes) -> bool:
        if isinstance(message, str):
            message = message.encode('utf-8')
        try:
            return self.scheme.verify(message, sig, pk)
        except Exception:
            return False


class HybridKEM:
    def classical_keygen(self):
        sk = X25519PrivateKey.generate()
        return sk, sk.public_key()

    def classical_exchange(self, my_sk, peer_pk):
        return my_sk.exchange(peer_pk)

    def pq_keygen(self):
        return Kyber768.keygen()

    def pq_encapsulate(self, pk):
        return Kyber768.enc(pk)

    def pq_decapsulate(self, sk, ct):
        return Kyber768.dec(sk, ct)

    def combine(self, classical_ss: bytes, pq_ss: bytes) -> bytes:
        hkdf = HKDF(
            algorithm=SHA256(),
            length=32,
            salt=None,
            info=b'hybrid-kem-v1'
        )
        return hkdf.derive(classical_ss + pq_ss)


if __name__ == '__main__':
    kem = KyberKEM()
    pk, sk = kem.keygen()
    ct, ss_alice = kem.encapsulate(pk)
    ss_bob = kem.decapsulate(sk, ct)

    signer = SphincsSigner(variant='small')
    pk_s, sk_s = signer.keygen()
    msg = b'GMIU PQC Assignment 2025 - Tirth Somani'
    sig = signer.sign(sk_s, msg)
    valid = signer.verify(pk_s, msg, sig)

    hybrid = HybridKEM()

    srv_x_sk, srv_x_pk = hybrid.classical_keygen()
    srv_k_pk, srv_k_sk = hybrid.pq_keygen()

    cli_x_sk, cli_x_pk = hybrid.classical_keygen()
    k_ct, pq_ss_c = hybrid.pq_encapsulate(srv_k_pk)
    x_ss_c = hybrid.classical_exchange(cli_x_sk, srv_x_pk)
    key_client = hybrid.combine(x_ss_c, pq_ss_c)

    pq_ss_s = hybrid.pq_decapsulate(srv_k_sk, k_ct)
    x_ss_s = hybrid.classical_exchange(srv_x_sk, cli_x_pk)
    key_server = hybrid.combine(x_ss_s, pq_ss_s)

    print("Kyber match:", ss_alice == ss_bob)
    print("SPHINCS valid:", valid)
    print("Hybrid match:", key_client == key_server)
