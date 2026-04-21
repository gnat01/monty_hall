import numpy as np
import matplotlib.pyplot as plt

# =========================
# PARAMETERS
# =========================
K = 50
m = 1
V = 1

t = np.arange(0, K-1)

def S(t):
    return (K-1) / (K * (K-1 - t))

# =========================
# FIGURE 1: S(t)
# =========================
plt.figure(figsize=(6,4))
plt.plot(t, S(t), linewidth=2)
plt.title("S(t) vs t")
plt.xlabel("t (number of reveals)")
plt.ylabel("Expected success S(t)")
plt.grid(True)
plt.tight_layout()
plt.savefig("fig_S.png", dpi=300)
plt.close()

# =========================
# FIGURE 2: W(t)
# =========================
costs = [0.005, 0.02, 0.05]

plt.figure(figsize=(6,4))
for c in costs:
    W = S(t) - c * t
    plt.plot(t, W, linewidth=2, label=f"c = {c}")

plt.axhline(0)
plt.title("W(t) vs t for multiple costs")
plt.xlabel("t")
plt.ylabel("Net value W(t)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fig_W.png", dpi=300)
plt.close()

# =========================
# FIGURE 3: t* vs c
# =========================
#c_vals = np.linspace(0.001, 0.06, 200)

c_vals = np.concatenate([
    np.linspace(0.001, 0.015, 100),
    np.linspace(0.015, 0.025, 500),   # dense around transition
    np.linspace(0.025, 0.06, 100)
])

t_star = []

for c in c_vals:
    W = S(t) - c * t
    t_star.append(t[np.argmax(W)])

plt.figure(figsize=(6,4))
plt.plot(c_vals, t_star, linewidth=2)
plt.title("Optimal t* vs cost c")
plt.xlabel("Cost c")
plt.ylabel("Optimal number of reveals t*")
plt.grid(True)
plt.tight_layout()
plt.savefig("fig_tstar.png", dpi=300)
plt.close()

print("Plots generated: fig_S.png, fig_W.png, fig_tstar.png")
