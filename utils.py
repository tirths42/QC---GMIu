"""
utils.py  —  Helper functions for BB84 QKD Simulation
======================================================
Student : Tirth Somani  |  Enrollment : 2023050905090529
"""

import random
import hashlib

# ── Bases and Bit constants ────────────────────────────────────────────────────
RECTILINEAR = '+'   # {0° = |0>, 90° = |1>}
DIAGONAL    = 'x'   # {45° = |+>, 135° = |->}


def random_bits(n: int) -> list:
    """Generate n random classical bits (0 or 1)."""
    return [random.randint(0, 1) for _ in range(n)]


def random_bases(n: int) -> list:
    """Generate n random bases ('+' or 'x')."""
    return [random.choice([RECTILINEAR, DIAGONAL]) for _ in range(n)]


def encode_qubit(bit: int, basis: str) -> dict:
    """
    Simulate qubit encoding.
    Returns a dict representing the qubit state.
      Rectilinear: 0 -> |0>, 1 -> |1>
      Diagonal:    0 -> |+>, 1 -> |->
    """
    return {"bit": bit, "basis": basis}


def measure_qubit(qubit: dict, basis: str) -> int:
    """
    Simulate qubit measurement.
    - If basis matches encoding basis: perfect measurement (return original bit).
    - If basis differs: random result (50/50).
    """
    if qubit["basis"] == basis:
        return qubit["bit"]
    else:
        return random.randint(0, 1)


def compute_qber(alice_bits: list, bob_bits: list, sample_idx: list) -> float:
    """
    Compute Quantum Bit Error Rate on the sampled positions.
    QBER = (number of mismatches) / (sample size)
    """
    if not sample_idx:
        return 0.0
    errors = sum(alice_bits[i] != bob_bits[i] for i in sample_idx)
    return errors / len(sample_idx)


def parity_reconcile(alice_bits: list, bob_bits: list,
                     block_size: int = 8, verbose: bool = False):
    """
    Simplified Cascade-like error correction using parity checks.
    Splits key into blocks; if parities differ, flip Bob's last bit in that block.
    Returns corrected Alice list, corrected Bob list, and number of fixed blocks.
    """
    alice_out  = list(alice_bits)
    bob_out    = list(bob_bits)
    fixed      = 0

    n = len(alice_out)
    for start in range(0, n, block_size):
        end          = min(start + block_size, n)
        a_parity     = sum(alice_out[start:end]) % 2
        b_parity     = sum(bob_out[start:end])   % 2
        if a_parity != b_parity:
            # flip last bit of Bob's block as correction
            bob_out[end - 1] ^= 1
            fixed += 1

    return alice_out, bob_out, fixed


def privacy_amplify(bits: list, qber: float) -> str:
    """
    Privacy amplification via SHA-256 universal hashing.
    Key is shortened proportional to estimated information leaked.
    Output is a hex-string of the compressed key.
    """
    bit_str    = ''.join(map(str, bits))
    raw_bytes  = bit_str.encode('utf-8')
    digest     = hashlib.sha256(raw_bytes).hexdigest()

    # Compression: keep (1 - 2*QBER) fraction of hash bits (min 32 chars)
    keep_chars = max(32, int(len(digest) * max(0.1, 1 - 2 * qber)))
    return digest[:keep_chars]


def print_banner(title: str):
    border = "=" * 60
    print(f"\n{border}")
    print(f"  {title}")
    print(f"{border}")


def print_step(n: int, title: str):
    print(f"\n  ── Stage {n}: {title} {'─'*(40-len(title))}")
