import sys
import time
import pyads
from datetime import datetime 

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

f = open(datetime.now().strftime("misure_LS180_%Y-%m-%d_%H-%M.csv"), "w")
f.write("target_y,direction,actual_y\n")

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

def acquire_data(plc, target_y, direction):
    for i in range(30):
        actual_y = plc.read_by_name("MAIN.axis_y.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        f.write(f"{target_y},{direction},{actual_y}\n")
        time.sleep(0.1)

def take_the_stairs(plc, start_position, step_size_mm):
    wait_for_movement_done(plc)
    for i in range(1, 11):
        target_y = start_position + i * step_size_mm
        move_y_axis(plc, target_y)
        wait_for_movement_done(plc)
        time.sleep(5)
        acquire_data(plc, target_y, "up")
    for i in range(9, 0, -1):
        target_y = start_position + i * step_size_mm
        move_y_axis(plc, target_y)
        wait_for_movement_done(plc)
        time.sleep(5)
        acquire_data(plc, target_y, "down")

# setting x axis to mid-range position
target_x = 300.0
move_x_axis(plc, target_x)
wait_for_movement_done(plc)

# positioning and measurements with y axis
positions = [100.0, 150.0, 200.0]
step_size = 0.0003  # 300 nanometers

for pos in positions:
    move_y_axis(plc, pos)
    wait_for_movement_done(plc)
    take_the_stairs(plc, pos, step_size)

# moving back y axis to mid-range position
target_y = 150.0
move_y_axis(plc, target_y)
wait_for_movement_done(plc)

f.close()
plc.close()
