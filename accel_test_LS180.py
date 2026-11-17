import pyads
import pylot
import time

VEL = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
Y_START = [50.0, 100.0, 150.0, 200.0]
CRUISE_VEL = 8.0
STEP_TIME = 3.0

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection(plc_netid, plc_port, plc_ip)
plc.open()

# Returning x axis to mid-range position
pylot.set_velocity(plc, CRUISE_VEL)
pylot.move_home_x_axis(plc)

for vel in VEL:
    step_distance = vel * STEP_TIME

    for y_start in Y_START:
        # Reaching start position
        pylot.set_velocity(plc, CRUISE_VEL)
        pylot.move_wait_y_axis(plc, y_start)
        time.sleep(2)

        # Doing the step
        pylot.set_velocity(plc, vel)
        pylot.move_wait_y_axis(plc, y_start + step_distance)
        time.sleep(2)

# Returning both axes to mid-range positions
pylot.set_velocity(plc, CRUISE_VEL)
pylot.move_home_xy_axes(plc)

plc.close()