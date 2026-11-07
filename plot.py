import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

a = pd.read_csv("results.csv")
b = pd.read_csv("results_hvt.csv")

fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))

for v in [1.62, 1.8, 1.98]:
    d = b[(b.process == "tt") & (b.vdd_V == v)]
    ax[0].plot(d.temp_C, d.tp_avg_ps, "o-", label=f"{v} V")
ax[0].set(title="Delay vs temperature (tt, HVT PMOS)", xlabel="Temp (°C)", ylabel="Avg delay (ps)")
ax[0].legend()

for name, d in [("plain PMOS", a), ("HVT PMOS", b)]:
    s = d[(d.process == "tt") & (d.vdd_V == 1.8)]
    ax[1].semilogy(s.temp_C, s.leak_in1_pA, "o-", label=name)
ax[1].set(title="Input-high leakage (tt, 1.8 V)", xlabel="Temp (°C)", ylabel="Leakage (pA)")
ax[1].legend()

for p in ["ss", "tt", "ff"]:
    s = b[(b.process == p) & (b.vdd_V == 1.8)]
    ax[2].plot(s.temp_C, s.tp_avg_ps, "o-", label=p)
ax[2].set(title="Process corners (HVT PMOS, 1.8 V)", xlabel="Temp (°C)", ylabel="Avg delay (ps)")
ax[2].legend()

plt.tight_layout()
plt.savefig("characterization.png", dpi=150)
print("saved characterization.png")
