import time
import pyads

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

n = 10000
tempi = []

for i in range(n):
    t0 = time.perf_counter()
    plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
    tempi.append(time.perf_counter() - t0)

plc.close()

print(f"letture:  {n}")
print(f"media:    {sum(tempi) / n * 1000:.3f} ms")
print(f"min:      {min(tempi) * 1000:.3f} ms")
print(f"max:      {max(tempi) * 1000:.3f} ms")
print(f"frequenza: {n / sum(tempi):.0f} letture/s")
