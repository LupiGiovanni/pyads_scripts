import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import pyads
import nidaqmx
from datetime import datetime
from nidaqmx.constants import TaskMode, AccelUnits, AccelSensitivityUnits, AcquisitionType
from nidaqmx.system import System, Device

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

# parametri test
velocities = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]  # mm/s
move_time = 5.0                          # s, distanza = velocity * move_time
x_starts = [100.0, 200.0, 300.0, 400.0]  # mm
y_starts = [50.0, 100.0, 150.0, 200.0]   # mm

if max(velocities) > 10.0:
    print("ERROR: velocità massima 10 mm/s")
    sys.exit(1)

# parametri accelerometri
daq_ip = "192.168.34.116"         # IP dello chassis cDAQ-9189
fs = 6000                          # frequenza di campionamento [Hz]
sens_board = [1054, 1000, 987.87]  # mV/g, triassiale sulla board (x, y, z)
sens_bench = 987.87                # mV/g, asse z sul banco (VERIFICARE)
duration = move_time + 4           # s, 2 s prima + movimento + 2 s dopo
n_samples = int(duration * fs)

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

# connessione allo chassis: lo aggiunge solo se non è già presente su questo PC
def connect_daq(ip):
    for dev in System.local().devices:
        try:
            if dev.tcpip_ethernet_ip == ip:
                print(f"Chassis già presente: {dev.name}")
                dev.reserve_network_device(override_reservation=True)
                return dev.name
        except nidaqmx.errors.DaqError:
            pass  # dispositivo non di rete (es. moduli), lo salto
    print(f"Aggiungo lo chassis {ip}")
    dev = Device.add_network_device(ip)
    dev.reserve_network_device(override_reservation=True)
    return dev.name

def wait_for_modules(chass, timeout=30):
    # dopo la riservazione i moduli compaiono con qualche secondo di ritardo
    t0 = time.time()
    while time.time() - t0 < timeout:
        moduli = [d.name for d in Device(chass).chassis_module_devices]
        if len(moduli) >= 2:
            print(f"Moduli: {moduli}")
            return
        time.sleep(1)
    print(f"ERROR: moduli non trovati nello chassis {chass}")
    sys.exit(1)

chass = connect_daq(daq_ip)
print(f"Chassis: {chass}")
wait_for_modules(chass)

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

# little helper functions
def move_xy(plc, target_x, target_y):
    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def wait_for_movement_done(plc):
    time.sleep(0.2)
    state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)
    while state != 0:
        if state == 3:
            print("ERROR")
            plc.close()
            sys.exit(1)
        time.sleep(0.2)
        state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)

with nidaqmx.Task() as task:
    for i in range(3):
        task.ai_channels.add_ai_accel_chan(f'{chass}Mod1/ai{i}', units=AccelUnits.METERS_PER_SECOND_SQUARED,
                                           sensitivity=sens_board[i], sensitivity_units=AccelSensitivityUnits.MILLIVOLTS_PER_G,
                                           min_val=-20, max_val=20)
    task.ai_channels.add_ai_accel_chan(f'{chass}Mod2/ai0', units=AccelUnits.METERS_PER_SECOND_SQUARED,
                                       sensitivity=sens_bench, sensitivity_units=AccelSensitivityUnits.MILLIVOLTS_PER_G,
                                       min_val=-20, max_val=20)
    task.timing.cfg_samp_clk_timing(fs, sample_mode=AcquisitionType.FINITE, samps_per_chan=n_samples)
    task.control(TaskMode.TASK_COMMIT)
    print('Sensor under stabilization')
    time.sleep(20)

    risultati = []
    for velocity in velocities:
        plc.write_by_name("MAIN.velocity", velocity, pyads.PLCTYPE_LREAL)
        distance = velocity * move_time

        for x0, y0 in zip(x_starts, y_starts):
            # positioning
            move_xy(plc, x0, y0)
            wait_for_movement_done(plc)
            time.sleep(5)

            # diagonal movement with acquisition
            print(f"v = {velocity:g} mm/s: ({x0}, {y0}) -> ({x0 + distance}, {y0 + distance})")
            task.start()
            time.sleep(2)
            move_xy(plc, x0 + distance, y0 + distance)
            dati = np.asarray(task.read(number_of_samples_per_channel=n_samples, timeout=duration + 5))
            task.stop()
            wait_for_movement_done(plc)

            t = np.arange(n_samples) / fs
            np.savetxt(f"diag_v{velocity:g}_x{x0:g}_y{y0:g}_{stamp}.csv", np.column_stack((t, dati.T)), delimiter=",",
                       header="time,board_x,board_y,board_z,bench_z", comments="")
            risultati.append((velocity, x0, y0, t, dati))

# moving back to mid-range position
move_xy(plc, 300.0, 150.0)
wait_for_movement_done(plc)

plc.close()

# plots: una figura per velocità, un riquadro per punto di partenza
labels = ["board_x", "board_y", "board_z", "bench_z"]
for velocity in velocities:
    fig, axs = plt.subplots(2, 2)
    fig.suptitle(f"v = {velocity:g} mm/s")
    punti = [r for r in risultati if r[0] == velocity]
    for ax, (v, x0, y0, t, dati) in zip(axs.flat, punti):
        for i in range(4):
            ax.plot(t, dati[i, :], label=labels[i])
        ax.set_title(f"partenza ({x0:g}, {y0:g})")
        ax.set_xlabel("tempo [s]")
        ax.set_ylabel("acc [m/s^2]")
    axs[0, 0].legend()
    fig.tight_layout()
plt.show()
