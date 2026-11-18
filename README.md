# pyads scripts

These are a series of Python scripts that use pyads library to communicate with PLC code. <br>
These scripts in particular aim to characterize PI LS270, PI LS180 and PI RS40 used in MORFEO.

- **LS270**: linear stage, x axis of the bench (`MAIN.axis_x`)
- **LS180**: linear stage, y axis of the bench (`MAIN.axis_y`)
- **RS40**: rotation stage (`MAIN.axis_rot`)

All scripts connect to the PLC at AMS NetId `5.36.211.100.1.1`, port 851 (port 500 for the NC), IP `192.168.34.130`, and move the axes through `pylot.py`. The measurements and their description are in `meas/` and `README_MEAS.md`.

## Scripts

### PLC programs (TwinCAT, Structured Text)

| File | Description |
| --- | --- |
| `PLC_assi_indipendenti.st` | x and y axes moved with `MC_MoveAbsolute`, each one independently, to `target_x` / `target_y` when `execute` is set. |
| `PLC_retta.st` | Same as above, but velocity, acceleration, deceleration and jerk of each axis are scaled so that both axes arrive together (straight line). |
| `PLC_rotational.st` | RS40 moved with `MC_MoveRelative` by `distance` at `velocity` when `execute` is set. |

### Python scripts

| File | Axis | Description |
| --- | --- | --- |
| `pylot.py` | all | Small library with the common functions to move the axes (see below). |
| `home_test_LS270_LS180.py` | x, y | Moves both axes to the mid-range position (300, 150) mm. |
| `MIM_LS270.py` | x | Staircase of 300 nm steps (10 up, 9 down) at 5 base positions (100–500 mm). At each step waits 5 s and reads the actual position 30 times. |
| `MIM_LS180.py` | y | Same as above at 3 base positions (100, 150, 200 mm). |
| `cumulative_error_LS270.py` | x | 100 steps of 300 nm, forward only, starting from 300 mm. At each step waits 5 s and reads the actual position 30 times. |
| `cumulative_error_LS180.py` | y | Same as above starting from 150 mm. |
| `step_response_LS270.py` | x | 10 mm step at 10 mm/s from 3 positions (100, 300, 500 mm), recording set position, actual position and following error for 4 s. |
| `step_response_LS180.py` | y | Same as above from 3 positions (100, 150, 200 mm). |
| `step_response_RS40.py` | rot | 30 relative steps of 5° at 5 °/s, recording set position, actual position and following error for 3 s each. |
| `record_LS270.py` | x | Records set position, actual position and following error for a given time, without moving the axis (usage: `python record_LS270.py <seconds>`). Useful for movements commanded from elsewhere, e.g. the TwinCAT GUI. |
| `record_LS180.py` | y | Same as above. |
| `record_RS40.py` | rot | Same as above. |
| `velocity_curve_LS270.py` | x | Open-loop velocity curve: through the NC (port 500) drives the axis with output 1–20 % and reads the actual velocity. Returns to mid-range after each point. **Do not go above 25 %.** |
| `velocity_curve_LS180.py` | y | Same as above. |
| `velocity_curve_RS40.py` | rot | Same as above with output 1–100 %. |
| `accel_test_LS270.py` | x | Vibration test with the WebDAQ 504 (REST API at `192.168.34.61`): records 5 s of background noise, then for 13 velocities (4–10 mm/s) and 4 start positions makes a move of 3 s at that velocity while acquiring. Data saved in `meas_LS270/`. |
| `accel_test_LS180.py` | y | Same as above. Data saved in `meas_LS180/`. |
| `accel_test_diagonal_LS180_LS270.py` | x, y | Same as above with both axes moving together (diagonal). Data saved in `meas_diag/`. |
| `edoardo_accel_test.py` | x, y | Older diagonal vibration test with the NI cDAQ-9189 (`nidaqmx`): moves of 5 s, 4 accelerometer channels, plots at the end. |
| `speed_test.py` | – | Measures the ADS read speed (10000 reads of one variable: mean, min, max, reads/s). |

## pylot

`pylot.py` collects the functions that every script used to copy at the beginning (move an axis, wait for the end of the movement, set the velocity), so that all the scripts use the same interface and the same safety checks.

### Example

```python
import pyads
import pylot

plc = pyads.Connection("5.36.211.100.1.1", 851, "192.168.34.130")
plc.open()

try:
    pylot.set_velocity(plc, 8.0)
    pylot.move_home_xy_axes(plc)
    pylot.move_wait_x_axis(plc, 100.0)
    # [...]

finally:
    plc.close()
```

### PLC variables used

`pylot` only reads and writes these variables of the `MAIN` program, so the PLC program running must have them:

| Variable | Type | Use |
| --- | --- | --- |
| `MAIN.target_x`, `MAIN.target_y` | LREAL | target position of x and y axes (mm) |
| `MAIN.distance` | LREAL | relative movement of the rotation stage (°) |
| `MAIN.velocity` | LREAL | velocity of the movement |
| `MAIN.execute` | BOOL | starts the movement |
| `MAIN.state` | INT | 0 = waiting, 1 = moving, 2 = done, 3 = error |

The x/y functions need an x/y PLC program (`PLC_assi_indipendenti.st` or `PLC_retta.st`); the rotational functions need `PLC_rotational.st`.

### Limits

| Constant | Value | Meaning |
| --- | --- | --- |
| `X_MIN`, `X_MAX` | 30.0, 570.0 mm | allowed range of the x axis |
| `Y_MIN`, `Y_MAX` | 30.0, 270.0 mm | allowed range of the y axis |
| `VELOCITY_MAX` | 10.0 | maximum velocity accepted by `set_velocity` |
| `MOVE_TIMEOUT` | 120.0 s | maximum time waited by `wait_for_movement_done` |

A target outside the range or a velocity outside (0, `VELOCITY_MAX`] is not sent to the PLC: the function raises `MotionError` instead.

### Functions

| Function | Description |
| --- | --- |
| `move_x_axis(plc, target_x)` | Sends x to `target_x` and returns immediately. |
| `move_y_axis(plc, target_y)` | Sends y to `target_y` and returns immediately. |
| `move_xy_axes(plc, target_x, target_y)` | Sends both axes and returns immediately. |
| `move_rotational_axis(plc, distance)` | Moves the rotation stage by `distance` (relative) and returns immediately. |
| `move_wait_x_axis`, `move_wait_y_axis`, `move_wait_xy_axes`, `move_wait_rotational_axis` | Same as above, but wait until the movement is done. |
| `move_home_x_axis(plc)` | Moves x to 300 mm and waits. |
| `move_home_y_axis(plc)` | Moves y to 150 mm and waits. |
| `move_home_xy_axes(plc)` | Moves both axes to (300, 150) mm and waits. |
| `wait_for_movement_done(plc, timeout=MOVE_TIMEOUT)` | Reads `MAIN.state` every 0.2 s until it is 0. Raises `MotionError` if the PLC goes in error (`state = 3`) or after `timeout` seconds. |
| `set_velocity(plc, value)` | Writes `MAIN.velocity`, after checking the limit. |
| `get_velocity(plc)` | Reads `MAIN.velocity`. |
| `write_into_memory(connection, index_group, index_offset, data)` | Writes raw bytes at an ADS index group/offset. Used with the NC connection (port 500) in the velocity curve scripts. **Use with caution.** |

Notes:

- The `move_*` functions without `wait` are used when the script must record data during the movement (e.g. `step_response_*`): after them call `wait_for_movement_done` before the next movement, otherwise the PLC ignores the new command.
- `move_rotational_axis` has no range check.
- Since `pylot` raises `MotionError` instead of closing the script, put the measurement inside `try` / `finally: plc.close()` (and `with open(...)` for the output file), as in the existing scripts.
