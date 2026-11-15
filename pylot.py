import pyads
import time
import sys

X_MIN = 30.0
X_MAX = 570.0
Y_MIN = 30.0
Y_MAX = 270.0
VELOCITY_MAX = 10.0

#   Y=300 -- +-------------------------------------------------------------------+
#            |                                                                   |
#            |                                                                   |
#   Y=270 -- |     +-------------------------------------------------------+     |
#            |     |                                                       |     |
#            |     |                                                       |     |
#            |     |                    RANGE ABILITATO                    |     |
#            |     |                                                       |     |
#            |     |                                                       |     |
#   Y=30  -- |     +-------------------------------------------------------+     |
#            |                                                                   |
#            |                                                                   |
#   Y=0   -- +-------------------------------------------------------------------+
#            |     |                                                       |     |
#            |     |                                                       |     |
#           X=0   X=30                                                 X=570   X=600

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

def move_x_axis(plc, target_x):
    if target_x < X_MIN | target_x > X_MAX
        print ("ERROR: attempted to run 'move_x_axis()' but 'target_x' was out of range")
        return
    
    plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)
    
def move_y_axis(plc, target_y):
    if target_y < Y_MIN | target_y > Y_MAX
            print ("ERROR: attempted to run 'move_y_axis()' but 'target_y' was out of range")
            return
    plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)

def move_rotational_axis (plc, distance):
    plc.write_by_name("MAIN.distance", distance, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)    

def move_home_x_axis(plc):
    move_x_axis(plc, 300.0)

def move_home_y_axis(plc):
    move_y_axis(plc, 150.0)

def move_home_xy_axes(plc):
    plc.write_by_name("MAIN.target_x", 300.0, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.target_y", 150.0, pyads.PLCTYPE_LREAL)
    plc.write_by_name("MAIN.execute", True, pyads.PLCTYPE_BOOL)
    wait_for_movement_done(plc)

def set_velocity(plc, value):
    if value < 0 | value > VELOCITY_MAX:
        print("ERROR: attempted to run 'set_velocity()' but 'value' was out of range")
        return
    plc.write_by_name("MAIN.velocity", value, pyads.PLCTYPE_LREAL)

def get_velocity(plc):
    return plc.read_by_name("Main.velocity", pyads.PLCTYPE_LREAL)

def write_into_memory(connection, index_group, index_offset, data):
    connection.write(index_group, index_offset, data, pyads.PLCTYPE_BYTE * len(data))