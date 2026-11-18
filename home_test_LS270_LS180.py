import pyads
import pylot

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

plc = pyads.Connection (plc_netid, plc_port, plc_ip)
plc.open()

pylot.move_home_xy_axes(plc)

plc.close()
