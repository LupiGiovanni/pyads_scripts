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

f = open(f"gradino_LS270_{stamp}.csv", "w")
f.write("start_x,time,actual_x\n")

ft = open(f"temperature_gradino_LS270_{stamp}.csv", "w")
ft.write("time_s,clock,temp_motor,temp_ambient\n")

t_start = time.perf_counter()
last_temp_time = -1.0

# little helper functions
def log_temp(plc):
    global last_temp_time
    now = time.perf_counter() - t_start
    if now - last_temp_time >= 1.0:
        temp_motor = plc.read_by_name("MAIN.temp_motor", pyads.PLCTYPE_INT)
        temp_ambient = plc.read_by_name("MAIN.temp_ambient", pyads.PLCTYPE_INT)
        clock = datetime.now().strftime("%H:%M:%S")
        ft.write(f"{now},{clock},{temp_motor},{temp_ambient}\n")
        ft.flush()
        last_temp_time = now

def pause(plc, seconds):
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < seconds:
        log_temp(plc)
        time.sleep(0.1)

def close_all():
    f.close()
    ft.close()
    plc.close()

def move_x_axis(plc, target_x):
    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def move_y_axis(plc, target_y):
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)

def wait_for_movement_done(plc):
    pause(plc, 0.2)
    state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)
    while state != 0:
        if state == 3:
            print("ERROR")
            close_all()
            sys.exit(1)
        pause(plc, 0.2)
        state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)

def step_and_record(plc, start_x, step_mm):
    move_x_axis(plc, start_x + step_mm)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 4.0:
        actual_x = plc.read_by_name("MAIN.axis_x.NcToPlc.ActPos", pyads.PLCTYPE_LREAL)
        f.write(f"{start_x},{time.perf_counter() - t0},{actual_x}\n")
        log_temp(plc)

log_temp(plc)

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
    pause(plc, 10)
    step_and_record(plc, pos, step_size)
    wait_for_movement_done(plc)

# moving back x axis to mid-range position
move_x_axis(plc, 300.0)
wait_for_movement_done(plc)

close_all()
