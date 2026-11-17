import os
import time
from datetime import datetime
import numpy as np
import pyads
import pylot
import requests

VEL = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
Y_START = [50.0, 100.0, 150.0, 200.0]
CRUISE_VEL = 8.0
STEP_TIME = 3.0

api = "http://192.168.34.61/api/v1.0"
out_dir = "meas_LS180"
stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

os.makedirs(out_dir, exist_ok=True)

# job name, channels and sample rate from the WebDAQ schedule
job = requests.get(api + "/schedule/descriptor").json()["jobs"][0]
desc = requests.get(api + f"/schedule/jobs/{job}/descriptor").json()
channels = [ch["name"] for ch in desc["channels"]]
fs = float(desc["acquisition"]["sample"]["rate"])
print(f"Job: {job}, canali: {channels}, fs = {fs:g} Hz")


def start_daq():
    requests.post(api + "/schedule/status", json={"run": True})


def stop_and_save(filename):
    # stops the acquisition, reads the job data from the WebDAQ memory and saves it to CSV
    requests.post(api + "/schedule/status", json={"run": False})
    time.sleep(1)
    n = int(requests.get(api + f"/schedule/jobs/{job}/status").json()["samplesAcquired"])
    blocks = []
    i = 0
    while i < n:
        count = min(10000, n - i)   # max 10000 samples per channel per call
        r = requests.get(api + f"/schedule/jobs/{job}/samples/{i}/{count}/bin")
        blocks.append(np.frombuffer(r.content, dtype="<f8").reshape(-1, len(channels)))
        i += count
    data = np.vstack(blocks)
    t = np.arange(len(data)) / fs
    np.savetxt(os.path.join(out_dir, filename), np.column_stack((t, data)), delimiter=",",
               header="time," + ",".join(channels), comments="")
    print(f"  salvato {filename} ({len(data)} campioni)")


plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

# Returning x axis to mid-range position
pylot.set_velocity(plc, CRUISE_VEL)
pylot.move_home_x_axis(plc)
time.sleep(2)

# Acquiring background noise
start_daq()
time.sleep(5)
stop_and_save(f"noise_LS180_{stamp}.csv")

for vel in VEL:
    step_distance = vel * STEP_TIME

    for y_start in Y_START:
        # Reaching start position
        pylot.set_velocity(plc, CRUISE_VEL)
        pylot.move_wait_y_axis(plc, y_start)
        time.sleep(2)

        # Doing the step
        print(f"v = {vel:g} mm/s: {y_start:g} -> {y_start + step_distance:g}")
        pylot.set_velocity(plc, vel)
        start_daq()
        time.sleep(3)
        pylot.move_wait_y_axis(plc, y_start + step_distance)
        time.sleep(3)
        stop_and_save(f"accel_LS180_v{vel:g}_y{y_start:g}_{stamp}.csv")

# Returning both axes to mid-range positions
pylot.set_velocity(plc, CRUISE_VEL)
pylot.move_home_xy_axes(plc)

plc.close()