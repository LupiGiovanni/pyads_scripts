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

f = open(f"step_response_rotational_{stamp}.csv", "w")
f.write("start_pos,time,set_pos,actual_pos,following_error\n")

def move_distance (plc, distance):
    plc.write_by_name("MAIN.distance", distance, pyads.PLCTYPE_LREAL)
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
        
def step_and_record(plc, step_degrees):
    start_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
    move_distance(plc, step_degrees)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 5.0:
        set_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.SetPos", pyads.PLCTYPE_LREAL)
        actual_pos = plc.read_by_name("MAIN.axis_rot.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        following_error = plc.read_by_name("MAIN.axis_rot.NcToPlc.PosDiff", pyads.PLCTYPE_LREAL)
        f.write(f"{start_pos},{time.perf_counter() - t0},{set_pos},{actual_pos},{following_error}\n")
        
# setting velocity
plc.write_by_name("MAIN.velocity", 5.0, pyads.PLCTYPE_LREAL)

step_size = 5 # degrees

for i in range(1):
    time.sleep(5)
    step_and_record(plc, step_size)
    wait_for_movement_done(plc)
    
f.close()
plc.close()
