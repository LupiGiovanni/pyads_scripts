import pyads

plc_netid = "5.36.211.100.1.1"
plc_port = 851
plc_ip = "192.168.34.130"

execute = True
target_x = 300.0
target_y = 150.0

plc = pyads.Connection (plc_netid, plc_port, plc_ip)
plc.open()

plc.write_by_name("MAIN.target_x", target_x, pyads.PLCTYPE_LREAL)
plc.write_by_name("MAIN.target_y", target_y, pyads.PLCTYPE_LREAL)
plc.write_by_name("MAIN.execute", execute, pyads.PLCTYPE_BOOL)

plc.close()
