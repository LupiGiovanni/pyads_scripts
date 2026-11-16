import pyads
import time


X_MIN = 30.0
X_MAX = 570.0
Y_MIN = 30.0
Y_MAX = 270.0
VELOCITY_MAX = 10.0
MOVE_TIMEOUT = 120.0


# Example of use:
# 
# import pyads
# import pylot
#
# plc_netid = "5.36.211.100.1.1"
# plc_port = 851
# plc_ip = "192.168.34.130"
# 
# plc = pyads.Connection(plc_netid, plc_port, plc_ip)
# plc.open()
#
# try:
#     set_velocity(plc, 8.0)
#     move_home_x_axis(plc)
#     move_home_y_axis(plc)
#     [...]
#
# finally:
#     plc.close()
#
#
#         300-- +-------------------------------------------------------------------+
#               |                                                                   |
#               |                                                                   |
#         270-- |     +-------------------------------------------------------+     |
#               |     |                                                       |     |
#               |     |                                                       |     |
# Y (mm)        |     |                    RANGE ABILITATO                    |     |
#               |     |                                                       |     |
#               |     |                                                       |     |
#          30-- |     +-------------------------------------------------------+     |
#               |                                                                   |
#               |                                                                   |
#           0-- +-------------------------------------------------------------------+
#
#               |     |                                                       |     |
#               0    30                                                      570   600
#
#                                              X (mm)


class MotionError(Exception):
    pass


def wait_for_movement_done(plc, timeout=MOVE_TIMEOUT):
    time.sleep(0.2)
    t0 = time.time()
    state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)
    while state != 0:
        if state == 3:
            raise MotionError("il PLC e' in stato di errore (MAIN.state = 3)")
        if time.time() - t0 > timeout:
            raise MotionError(f"timeout: movimento non terminato dopo {timeout} s")
        time.sleep(0.2)
        state = plc.read_by_name("MAIN.state", pyads.PLCTYPE_INT)


def move_x_axis(plc, target_x):
    if not (X_MIN <= target_x <= X_MAX):
        raise MotionError(f"move_x_axis: target_x = {target_x} fuori range [{X_MIN}, {X_MAX}]")

    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)


def move_y_axis(plc, target_y):
    if not (Y_MIN <= target_y <= Y_MAX):
        raise MotionError(f"move_y_axis: target_y = {target_y} fuori range [{Y_MIN}, {Y_MAX}]")

    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)


def move_xy_axes(plc, target_x, target_y):
    if not (X_MIN <= target_x <= X_MAX):
        raise MotionError(f"move_xy_axes: target_x = {target_x} fuori range [{X_MIN}, {X_MAX}]")
    if not (Y_MIN <= target_y <= Y_MAX):
        raise MotionError(f"move_xy_axes: target_y = {target_y} fuori range [{Y_MIN}, {Y_MAX}]")

    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)
    

def move_rotational_axis(plc, distance):
    plc.write_by_name("MAIN.distance", distance, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)


def move_home_x_axis(plc):
    move_x_axis(plc, 300.0)


def move_home_y_axis(plc):
    move_y_axis(plc, 150.0)


def set_velocity(plc, value):
    if not (0 < value <= VELOCITY_MAX):
        raise MotionError(f"set_velocity: value = {value} fuori range (0, {VELOCITY_MAX}]")

    plc.write_by_name("MAIN.velocity", value, pyads.PLCTYPE_LREAL)


def get_velocity(plc):
    return plc.read_by_name("MAIN.velocity", pyads.PLCTYPE_LREAL)


def write_into_memory(connection, index_group, index_offset, data):
    connection.write(index_group, index_offset, data, pyads.PLCTYPE_BYTE * len(data))