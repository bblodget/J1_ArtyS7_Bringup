# Get command line arguments
set bitstream_file [lindex $argv 0]
set cable_name [lindex $argv 1]

# Open hardware manager and connect to the board
open_hw_manager
connect_hw_server
open_hw_target
current_hw_device [get_hw_devices xc7s50_0]
refresh_hw_device -update_hw_probes false [lindex [get_hw_devices xc7s50_0] 0]

# Program the device
set_property PROGRAM.FILE $bitstream_file [get_hw_devices xc7s50_0]
program_hw_devices [get_hw_devices xc7s50_0]

# Close hardware manager
close_hw_manager