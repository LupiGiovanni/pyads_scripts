import sys
import time
import pyads
from datetime import datetime

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

f = open(f"step_response_LS270_{stamp}.csv", "w")
f.write("start_x,time,actual_x\n")

# little helper functions
def move_x_axis(plc, target_x):
    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def move_y_axis(plc, target_y):
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def wait_for_movement_done(plc):
    time.sleep(0.2)
    state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)
    while state != 0:
        if state == 3:
            print("ERROR")
            f.close()
            plc.close()
            sys.exit(1)
        time.sleep(0.2)
        state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)

def step_and_record(plc, start_x, step_mm):
    move_x_axis(plc, start_x + step_mm)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 4.0:
        actual_x = plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        f.write(f"{start_x},{time.perf_counter() - t0},{actual_x}\n")

# setting velocity
plc.write_by_name("MAIN.velocity", 10.0, pyads.PLCTYPE_LREAL)

# setting y axis to mid-range position
move_y_axis(plc, 150.0)
wait_for_movement_done(plc)

positions = [100.0, 300.0, 500.0]
step_size = 10.0  # mm

for pos in positions:
    move_x_axis(plc, pos)
    wait_for_movement_done(plc)
    time.sleep(5)
    step_and_record(plc, pos, step_size)
    wait_for_movement_done(plc)

# moving back x axis to mid-range position
move_x_axis(plc, 300.0)
wait_for_movement_done(plc)

f.close()
plc.close()
