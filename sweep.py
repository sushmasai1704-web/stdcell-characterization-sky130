import subprocess, re, csv, os, itertools

LIB = "/home/sushma/.ciel/ciel/sky130/versions/0fe599b2afb6708d281543108caf8310912f54af/sky130A/libs.tech/ngspice/sky130.lib.spice"
NGSPICE = os.path.expanduser("~/ngspice-local/bin/ngspice")

PROCS = ["tt", "ss", "ff"]
VDDS = [1.62, 1.8, 1.98]
TEMPS = [-40, 25, 125]

TEMPLATE = """* inverter characterization
.lib {lib} {proc}
.temp {temp}
.options abstol=1e-15 gmin=1e-15
Vdd vdd 0 {vdd}
Vin in 0 PULSE(0 {vdd} 1n 100p 100p 5n 10n)
XMn out in 0   0   sky130_fd_pr__nfet_01v8 w=0.42 l=0.15
XMp out in vdd vdd sky130_fd_pr__pfet_01v8 w=0.84 l=0.15
Cl out 0 10f
.tran 10p 25n
.control
run
meas tran tpHL trig v(in) val={half} rise=1 targ v(out) val={half} fall=1
meas tran tpLH trig v(in) val={half} fall=1 targ v(out) val={half} rise=1
meas tran ileak_low avg i(vdd) from=0.2n to=0.9n
meas tran ileak_high avg i(vdd) from=4n to=6n
meas tran iavg avg i(vdd) from=1n to=21n
quit
.endc
.end
"""

def grab(text, name):
    m = re.search(r"^" + name + r"\s*=\s*([-+0-9.eE]+)", text, re.M | re.I)
    return float(m.group(1)) if m else None

rows = []
for proc, vdd, temp in itertools.product(PROCS, VDDS, TEMPS):
    net = TEMPLATE.format(lib=LIB, proc=proc, temp=temp, vdd=vdd, half=vdd / 2)
    with open("run.spice", "w") as f:
        f.write(net)
    r = subprocess.run([NGSPICE, "-b", "run.spice"], capture_output=True,
                       text=True, stdin=subprocess.DEVNULL, timeout=300)
    out = r.stdout + r.stderr
    tphl, tplh = grab(out, "tphl"), grab(out, "tplh")
    il, ih, ia = grab(out, "ileak_low"), grab(out, "ileak_high"), grab(out, "iavg")
    if None in (tphl, tplh, il, ih, ia):
        print(f"{proc} {vdd}V {temp}C: FAILED (see run.log)")
        open("run.log", "a").write(out + "\n")
        continue
    row = {
        "process": proc, "vdd_V": vdd, "temp_C": temp,
        "tpHL_ps": round(tphl * 1e12, 2),
        "tpLH_ps": round(tplh * 1e12, 2),
        "tp_avg_ps": round((tphl + tplh) / 2 * 1e12, 2),
        "leak_in0_pA": round(abs(il) * 1e12, 3),
        "leak_in1_pA": round(abs(ih) * 1e12, 3),
        "avg_power_uW": round(abs(ia) * vdd * 1e6, 4),
    }
    rows.append(row)
    print(row, flush=True)

if rows:
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print("Saved results.csv")
