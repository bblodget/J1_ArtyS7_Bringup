# Set up the project
create_project -force j1_sim ./j1_sim -part xc7s50csga324-1

# Add source files
add_files -norecurse ../j1-universal-16kb-dualport.v
add_files -norecurse ../stack2.v
add_files -norecurse ../stack3.v

# Add the IP
add_files -norecurse ../ip_repo/j1_memory/j1_memory.xci

# Add testbench
add_files -fileset sim_1 -norecurse j1_uart_tb.v

# Set j1_uart_tb as top module for simulation
set_property top j1_uart_tb [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]

# Set simulation options
set_property -name {xsim.simulate.runtime} -value {1000ns} -objects [get_filesets sim_1]
set_property -name {xsim.simulate.log_all_signals} -value {true} -objects [get_filesets sim_1]

# Create and configure wave window
launch_simulation -simset sim_1 -mode behavioral
add_wave /j1_uart_tb/*

# Run simulation and check for errors
set error_count 0
restart
run all

# Clean up
close_sim -force
close_project