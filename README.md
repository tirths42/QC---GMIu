# BB84 Quantum Key Distribution — Full End-to-End Simulation

**Student:** Tirth Somani  
**Enrollment No.:** 2023050905090529  
**Class:** G | **Branch:** B.Tech (Information Technology)  
**University:** Gujarat Metropolitan International University (GMiU)

---

## Overview

This repository contains a complete Python simulation of the **BB84 Quantum Key Distribution (QKD)** protocol, extended from the basic lab implementation to a full end-to-end pipeline:

| Stage | Module | Description |
|-------|--------|-------------|
| 1 | `bb84_qkd.py` | Raw key generation — Alice encodes qubits, Bob measures |
| 2 | `bb84_qkd.py` | Basis sifting — discard mismatched-basis bits |
| 3 | `bb84_qkd.py` + `eavesdrop_test.py` | QBER estimation & eavesdropping detection |
| 4 | `utils.py` → `parity_reconcile()` | Error correction via parity reconciliation |
| 5 | `utils.py` → `privacy_amplify()` | Privacy amplification via SHA-256 hashing |

---

## File Structure

```
bb84-qkd-simulation/
├── bb84_qkd.py          # Main simulation (all 5 stages)
├── utils.py             # Qubit encoding, measurement, QBER, error correction, PA
├── eavesdrop_test.py    # Eavesdropping detection experiments
├── generate_plots.py    # Visualisation — QBER charts & protocol flow diagram
├── README.md            # This file
└── BB84_QKD_Report.pdf  # Full reference report (PDF)
```

---

## How to Run

### Prerequisites
```bash
pip install matplotlib
```

### 1. Run Full Simulation
```bash
python bb84_qkd.py
```
Runs two scenarios: (a) No eavesdropper, (b) Eve intercepts all qubits.

### 2. Eavesdropping Detection Experiment
```bash
python eavesdrop_test.py
```
Runs 30 trials across 4 eavesdropping levels and reports QBER statistics.

### 3. Generate Plots
```bash
python generate_plots.py
```
Saves `qber_analysis.png` and `protocol_flow.png`.

---

## Key Concepts

- **BB84 Protocol:** First QKD protocol by Bennett & Brassard (1984). Uses two conjugate bases (+, x) to encode bits as qubit states.
- **QBER (Quantum Bit Error Rate):** Measures error rate in sifted key. QBER > 11% indicates eavesdropping.
- **Basis Sifting:** Only bits where Alice and Bob used the same basis are kept (~50% of raw bits).
- **Error Correction:** Parity-based reconciliation removes residual errors without revealing the key.
- **Privacy Amplification:** Universal hashing (SHA-256) compresses the key to remove any information Eve may have gained.

---

## Expected Output

| Scenario | Avg QBER | Key Established |
|----------|----------|-----------------|
| No Eve | ~0% | Yes |
| Eve 25% | ~6–8% | Likely Yes |
| Eve 50% | ~13–15% | Aborted |
| Eve 100% | ~24–26% | Aborted |

---

## References

1. Bennett, C. H. & Brassard, G. (1984). *Quantum Cryptography: Public Key Distribution and Coin Tossing*.
2. Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
3. Gisin, N. et al. (2002). *Quantum Cryptography*. Rev. Mod. Phys., 74, 145.
4. Python `hashlib` documentation — https://docs.python.org/3/library/hashlib.html
