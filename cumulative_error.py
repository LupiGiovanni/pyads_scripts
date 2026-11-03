import sys
import time
import pyads
from datetime import datetime 

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

f = open(datetime.now().strftime("errore_accumulato_LS270_%Y-%m-%d_%H-%M.csv"), "w")
f.write("target_x,actual_x,following_error\n")

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

def acquire_data(plc, target_x):
    for i in range(30):
        actual_x = plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_x.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{target_x},{actual_x},{following_error}\n")
        time.sleep(0.1)

def do_100_steps(plc, start_position, step_size_mm):
    wait_for_movement_done(plc)
    for i in range(1, 101):
        target_x = start_position + i * step_size_mm
        move_x_axis(plc, target_x)
        wait_for_movement_done(plc)
        time.sleep(5)
        acquire_data(plc, target_x)

# setting y axis to mid-range position
target_y = 150.0
move_y_axis(plc, target_y)
wait_for_movement_done(plc)

# positioning and measurements with x axis
positions = [100.0, 200.0, 300.0, 400.0, 500.0]
step_size = 0.0003  # 300 nanometers

for pos in positions:
    move_x_axis(plc, pos)
    wait_for_movement_done(plc)
    do_100_steps(plc, pos, step_size)

# moving back x axis to mid-range position
target_x = 300.0
move_x_axis(plc, target_x)
wait_for_movement_done(plc)

f.close()
plc.close()