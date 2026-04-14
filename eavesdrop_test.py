"""
eavesdrop_test.py  —  Eavesdropping Detection Experiments
==========================================================
Student : Tirth Somani  |  Enrollment : 2023050905090529

Runs multiple trials with and without Eve to compare QBER distributions.
"""

import random
from utils import (random_bits, random_bases, encode_qubit,
                   measure_qubit, compute_qber)

def simulate_channel(n_qubits=100, eve_fraction=0.0):
    """
    Simulate one complete BB84 transmission.
    Returns QBER measured after basis sifting.
    """
    alice_bits  = random_bits(n_qubits)
    alice_bases = random_bases(n_qubits)
    qubits      = [encode_qubit(b, basis) for b, basis in zip(alice_bits, alice_bases)]

    if eve_fraction > 0:
        n_intercept = int(n_qubits * eve_fraction)
        eve_bases   = random_bases(n_qubits)
        for i in range(n_intercept):
            measured   = measure_qubit(qubits[i], eve_bases[i])
            qubits[i]  = encode_qubit(measured, eve_bases[i])

    bob_bases = random_bases(n_qubits)
    bob_bits  = [measure_qubit(q, b) for q, b in zip(qubits, bob_bases)]

    # Sifting
    sifted_a, sifted_b = [], []
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            sifted_a.append(alice_bits[i])
            sifted_b.append(bob_bits[i])

    if len(sifted_a) < 4:
        return 0.0

    n_sample   = max(4, len(sifted_a) // 4)
    sample_idx = random.sample(range(len(sifted_a)), n_sample)
    return compute_qber(sifted_a, sifted_b, sample_idx)


def run_detection_experiment(trials=30, n_qubits=200):
    print("\n" + "="*60)
    print("  Eavesdropping Detection Experiment")
    print("="*60)

    scenarios = [
        ("No Eve  (0%  interception)",  0.00),
        ("Eve 25% interception",        0.25),
        ("Eve 50% interception",        0.50),
        ("Eve 100% interception",       1.00),
    ]

    for label, fraction in scenarios:
        qbers = [simulate_channel(n_qubits, fraction) for _ in range(trials)]
        avg   = sum(qbers) / len(qbers) * 100
        mn    = min(qbers) * 100
        mx    = max(qbers) * 100
        detected = sum(q > 0.11 for q in qbers)
        print(f"\n  {label}")
        print(f"    Avg QBER : {avg:5.2f}%  |  Min: {mn:.2f}%  |  Max: {mx:.2f}%")
        print(f"    Detected : {detected}/{trials} trials flagged as eavesdropped")


if __name__ == "__main__":
    run_detection_experiment()
