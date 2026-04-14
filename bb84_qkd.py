"""
bb84_qkd.py  —  Full End-to-End BB84 Quantum Key Distribution Simulation
=========================================================================
Student : Tirth Somani
Enroll  : 2023050905090529
Class   : G  |  Branch : B.Tech (I.T.)
=========================================================================

Stages implemented
------------------
1. Raw Key Generation      – Alice prepares qubits; Bob measures them
2. Basis Sifting           – Alice & Bob compare bases over public channel
3. Eavesdropping Detection – Sample a subset of sifted key to estimate QBER
4. Error Correction        – Cascade-like parity reconciliation (simplified)
5. Privacy Amplification   – Universal hashing via SHA-256 to shorten the key

Run:  python bb84_qkd.py
"""

import random
import hashlib
from utils import (
    random_bits, random_bases, encode_qubit, measure_qubit,
    compute_qber, parity_reconcile, privacy_amplify, print_banner, print_step
)

# ── Configuration ──────────────────────────────────────────────────────────────
N_QUBITS          = 200      # number of qubits Alice sends
SAMPLE_FRACTION   = 0.25     # fraction used for QBER estimation
QBER_THRESHOLD    = 0.11     # abort if QBER > 11 %
EVE_PRESENT       = False    # set True to simulate eavesdropper
EVE_INTERCEPT_PCT = 1.0      # fraction Eve intercepts (1.0 = all)


def run_bb84(n_qubits=N_QUBITS, eve=EVE_PRESENT, verbose=True):
    print_banner("BB84 Quantum Key Distribution — Full Simulation")

    # ── STAGE 1 : Raw Key Generation ──────────────────────────────────────────
    print_step(1, "Raw Key Generation")
    alice_bits  = random_bits(n_qubits)
    alice_bases = random_bases(n_qubits)

    # Alice encodes qubits
    qubits = [encode_qubit(b, basis) for b, basis in zip(alice_bits, alice_bases)]

    # Eve intercepts (optional)
    if eve:
        eve_bases   = random_bases(n_qubits)
        n_intercept = int(n_qubits * EVE_INTERCEPT_PCT)
        for i in range(n_intercept):
            qubits[i] = encode_qubit(
                measure_qubit(qubits[i], eve_bases[i]), eve_bases[i]
            )
        print(f"  [EVE] Eavesdropper intercepted {n_intercept}/{n_qubits} qubits.")

    # Bob measures
    bob_bases = random_bases(n_qubits)
    bob_bits  = [measure_qubit(q, b) for q, b in zip(qubits, bob_bases)]

    if verbose:
        print(f"  Alice bits (first 20) : {alice_bits[:20]}")
        print(f"  Alice bases(first 20) : {alice_bases[:20]}")
        print(f"  Bob   bases(first 20) : {bob_bases[:20]}")
        print(f"  Bob   bits (first 20) : {bob_bits[:20]}")

    # ── STAGE 2 : Basis Sifting ───────────────────────────────────────────────
    print_step(2, "Basis Sifting")
    sifted_alice, sifted_bob, match_indices = [], [], []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])
            match_indices.append(i)

    sift_rate = len(sifted_alice) / n_qubits * 100
    if verbose:
        print(f"  Matched bases : {len(sifted_alice)}/{n_qubits}  ({sift_rate:.1f}%)")
        print(f"  Sifted Alice  (first 20): {sifted_alice[:20]}")
        print(f"  Sifted Bob    (first 20): {sifted_bob[:20]}")

    # ── STAGE 3 : Eavesdropping Detection (QBER) ─────────────────────────────
    print_step(3, "Eavesdropping Detection — QBER Estimation")
    n_sample = max(4, int(len(sifted_alice) * SAMPLE_FRACTION))
    sample_idx = random.sample(range(len(sifted_alice)), n_sample)
    qber = compute_qber(sifted_alice, sifted_bob, sample_idx)

    # Remove sampled bits from key
    remaining_idx = [i for i in range(len(sifted_alice)) if i not in sample_idx]
    raw_key_alice = [sifted_alice[i] for i in remaining_idx]
    raw_key_bob   = [sifted_bob[i]   for i in remaining_idx]

    if verbose:
        print(f"  Sample size   : {n_sample} bits")
        print(f"  QBER          : {qber*100:.2f}%  (threshold {QBER_THRESHOLD*100:.0f}%)")

    if qber > QBER_THRESHOLD:
        print(f"\n  [ABORT] QBER too high ({qber*100:.2f}%) — possible eavesdropper!")
        print("  Protocol ABORTED. Key exchange failed.")
        return None, None, qber

    print(f"  [OK] QBER acceptable. Proceeding.")

    # ── STAGE 4 : Error Correction ────────────────────────────────────────────
    print_step(4, "Error Correction (Parity Reconciliation)")
    corrected_alice, corrected_bob, errors_fixed = parity_reconcile(
        raw_key_alice, raw_key_bob, verbose=verbose
    )

    if verbose:
        bits_before = sum(a != b for a, b in zip(raw_key_alice, raw_key_bob))
        bits_after  = sum(a != b for a, b in zip(corrected_alice, corrected_bob))
        print(f"  Errors before correction : {bits_before}")
        print(f"  Errors after  correction : {bits_after}")
        print(f"  Blocks reconciled        : {errors_fixed}")

    # ── STAGE 5 : Privacy Amplification ──────────────────────────────────────
    print_step(5, "Privacy Amplification (Universal Hashing)")
    final_key_alice = privacy_amplify(corrected_alice, qber)
    final_key_bob   = privacy_amplify(corrected_bob,   qber)

    match = (final_key_alice == final_key_bob)
    if verbose:
        print(f"  Final key length : {len(final_key_alice)} bits")
        print(f"  Alice final key  : {final_key_alice}")
        print(f"  Bob   final key  : {final_key_bob}")
        print(f"  Keys match       : {'YES - Secure key established!' if match else 'NO  - Key mismatch!'}")

    print("\n" + "="*60)
    status = "SUCCESS" if match else "MISMATCH"
    print(f"  QKD RESULT : {status}  |  QBER = {qber*100:.2f}%  |  Key bits = {len(final_key_alice)}")
    print("="*60)
    return final_key_alice, final_key_bob, qber


if __name__ == "__main__":
    # Normal run (no eavesdropper)
    print("\n>>> Scenario 1: No Eavesdropper\n")
    run_bb84(n_qubits=N_QUBITS, eve=False)

    print("\n\n>>> Scenario 2: Eve Intercepts All Qubits\n")
    run_bb84(n_qubits=N_QUBITS, eve=True)
