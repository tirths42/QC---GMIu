"""
generate_plots.py  —  Visualisations for BB84 QKD Report
=========================================================
Student : Tirth Somani  |  Enrollment : 2023050905090529
"""

import random
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

random.seed(42)

# ── Helpers (inline to keep script self-contained) ───────────────────────────
def sim_qber(n=200, eve_frac=0.0):
    alice_bits  = [random.randint(0,1) for _ in range(n)]
    alice_bases = [random.choice(['+','x']) for _ in range(n)]
    qubits      = [{"bit":b,"basis":bs} for b,bs in zip(alice_bits,alice_bases)]
    if eve_frac > 0:
        eve_bases = [random.choice(['+','x']) for _ in range(n)]
        for i in range(int(n*eve_frac)):
            eb  = eve_bases[i]
            bit = qubits[i]["bit"] if qubits[i]["basis"]==eb else random.randint(0,1)
            qubits[i] = {"bit":bit,"basis":eb}
    bob_bases = [random.choice(['+','x']) for _ in range(n)]
    bob_bits  = [q["bit"] if q["basis"]==b else random.randint(0,1)
                 for q,b in zip(qubits,bob_bases)]
    sa,sb=[],[]; 
    for i in range(n):
        if alice_bases[i]==bob_bases[i]:
            sa.append(alice_bits[i]); sb.append(bob_bits[i])
    if len(sa)<4: return 0.0
    idx = random.sample(range(len(sa)), max(4,len(sa)//4))
    return sum(sa[i]!=sb[i] for i in idx)/len(idx)


# ════════════════════════════════════════════════════════
# FIGURE 1 — Protocol Flow Diagram
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#f8fafc')
ax.set_facecolor('#f8fafc')
ax.set_xlim(0, 14); ax.set_ylim(0, 6); ax.axis('off')
ax.set_title("BB84 QKD Protocol — End-to-End Flow",
             fontsize=14, fontweight='bold', color='#1a3c6e', pad=10)

STAGES = [
    (1.1, "Stage 1\nRaw Key Gen",    '#2e86de', '#fff'),
    (3.5, "Stage 2\nBasis Sifting",  '#10ac84', '#fff'),
    (5.9, "Stage 3\nQBER / Eve Det", '#ee5a24', '#fff'),
    (8.3, "Stage 4\nError Correct",  '#8854d0', '#fff'),
    (10.7,"Stage 5\nPrivacy Amp.",   '#1289A7', '#fff'),
    (13.0,"Final\nSecret Key",       '#1a3c6e', '#fff'),
]
bw, bh = 1.9, 1.1
for x, label, fc, tc in STAGES:
    rect = mpatches.FancyBboxPatch((x-bw/2, 2.45), bw, bh,
        boxstyle="round,pad=0.08", linewidth=1.5,
        edgecolor='white', facecolor=fc, zorder=3)
    ax.add_patch(rect)
    ax.text(x, 3.0, label, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=tc, zorder=4)

for i in range(len(STAGES)-1):
    x1 = STAGES[i][0]   + bw/2
    x2 = STAGES[i+1][0] - bw/2
    ax.annotate('', xy=(x2, 3.0), xytext=(x1, 3.0),
                arrowprops=dict(arrowstyle='->', color='#555', lw=2), zorder=2)

# Alice / Bob / Eve labels
for lbl, y, color in [("Alice (Sender)", 4.7, '#2e86de'),
                       ("Bob (Receiver)", 1.3, '#10ac84'),
                       ("Eve (Attacker?)", 5.4, '#ee5a24')]:
    ax.text(7.0, y, lbl, ha='center', fontsize=10,
            fontweight='bold', color=color,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor=color, linewidth=1.2))

# Quantum channel arrow
ax.annotate('', xy=(3.0, 3.56), xytext=(1.5, 4.5),
            arrowprops=dict(arrowstyle='->', color='#2e86de', lw=1.5,
                            linestyle='dashed'))
ax.annotate('', xy=(3.0, 2.45), xytext=(1.5, 1.5),
            arrowprops=dict(arrowstyle='->', color='#10ac84', lw=1.5,
                            linestyle='dashed'))

# Eve intercept mark
ax.plot(3.5, 4.2, 'v', color='#ee5a24', markersize=12, zorder=5)
ax.text(3.5, 4.55, "Intercept?", ha='center', fontsize=7.5,
        color='#ee5a24', style='italic')

ax.text(7.0, 0.35, "Public Classical Channel  (basis comparison, parity, hash seeds)",
        ha='center', fontsize=8, color='#555', style='italic')
ax.axhline(y=0.7, xmin=0.04, xmax=0.96, color='#aaa', linewidth=1, linestyle=':')

plt.tight_layout()
plt.savefig("/home/claude/qkd_project/protocol_flow.png",
            dpi=150, bbox_inches='tight', facecolor='#f8fafc')
plt.close()
print("Saved: protocol_flow.png")


# ════════════════════════════════════════════════════════
# FIGURE 2 — QBER Distribution by Eve Interception Level
# ════════════════════════════════════════════════════════
trials   = 50
configs  = [0.0, 0.25, 0.50, 1.0]
labels   = ['No Eve\n(0%)', 'Eve 25%', 'Eve 50%', 'Eve 100%']
colors_b = ['#10ac84','#f9ca24','#e55039','#c0392b']

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor('#f8fafc')

# Left: box plot
data = [[sim_qber(200, f)*100 for _ in range(trials)] for f in configs]
bp = axes[0].boxplot(data, patch_artist=True, widths=0.55,
                     medianprops=dict(color='white', linewidth=2))
for patch, color in zip(bp['boxes'], colors_b):
    patch.set_facecolor(color)
    patch.set_alpha(0.85)
axes[0].axhline(y=11, color='red', linestyle='--', linewidth=1.5,
                label='QBER threshold (11%)')
axes[0].set_xticklabels(labels, fontsize=10)
axes[0].set_ylabel('QBER (%)', fontsize=11)
axes[0].set_title('QBER Distribution vs Eve Interception', fontsize=12, fontweight='bold')
axes[0].legend(fontsize=9); axes[0].grid(axis='y', alpha=0.3)
axes[0].set_facecolor('#f8fafc')

# Right: detection rate bar chart
detection_rates = [sum(q>11 for q in d)/trials*100 for d in data]
bars = axes[1].bar(labels, detection_rates, color=colors_b, alpha=0.85,
                   edgecolor='white', linewidth=1.2)
for bar, val in zip(bars, detection_rates):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
                 f'{val:.0f}%', ha='center', fontsize=10, fontweight='bold')
axes[1].set_ylabel('Detection Rate (%)', fontsize=11)
axes[1].set_title('Eavesdropping Detection Rate', fontsize=12, fontweight='bold')
axes[1].set_ylim(0, 115); axes[1].grid(axis='y', alpha=0.3)
axes[1].set_facecolor('#f8fafc')

plt.suptitle("BB84 QKD — QBER Analysis  (50 trials × 200 qubits)",
             fontsize=13, fontweight='bold', color='#1a3c6e', y=1.01)
plt.tight_layout()
plt.savefig("/home/claude/qkd_project/qber_analysis.png",
            dpi=150, bbox_inches='tight', facecolor='#f8fafc')
plt.close()
print("Saved: qber_analysis.png")


# ════════════════════════════════════════════════════════
# FIGURE 3 — Key Length vs Number of Qubits
# ════════════════════════════════════════════════════════
ns       = [50, 100, 150, 200, 300, 400, 500]
raw_lens, sifted_lens, final_lens = [], [], []

for n in ns:
    alice_bits  = [random.randint(0,1) for _ in range(n)]
    alice_bases = [random.choice(['+','x']) for _ in range(n)]
    bob_bases   = [random.choice(['+','x']) for _ in range(n)]
    sifted      = [i for i in range(n) if alice_bases[i]==bob_bases[i]]
    sl          = len(sifted)
    sample      = max(4, sl//4)
    remaining   = sl - sample
    # privacy amplification keeps ~64 chars hex = 256 bits, capped
    final       = min(64, remaining // 2)
    raw_lens.append(n)
    sifted_lens.append(sl)
    final_lens.append(final)

fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('#f8fafc')
ax.set_facecolor('#f8fafc')
ax.plot(ns, raw_lens,    'o-', color='#2e86de', lw=2, label='Raw qubits sent', markersize=7)
ax.plot(ns, sifted_lens, 's-', color='#10ac84', lw=2, label='Sifted key bits', markersize=7)
ax.plot(ns, final_lens,  '^-', color='#ee5a24', lw=2, label='Final key (after PA)', markersize=7)
ax.set_xlabel('Number of Qubits (N)', fontsize=11)
ax.set_ylabel('Key Length (bits / hex chars)', fontsize=11)
ax.set_title('Key Length vs Number of Qubits', fontsize=12, fontweight='bold', color='#1a3c6e')
ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("/home/claude/qkd_project/key_length_plot.png",
            dpi=150, bbox_inches='tight', facecolor='#f8fafc')
plt.close()
print("Saved: key_length_plot.png")
