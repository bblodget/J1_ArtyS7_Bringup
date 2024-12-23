# Set project directory and name
set proj_dir [file normalize "."]
set proj_name "j1_top"

# Create project
create_project ${proj_name} ${proj_dir}/${proj_name} -part xc7s50csga324-1

# Set project properties
set_property target_language Verilog [current_project]

# Set IP repository paths
set_property ip_repo_paths [file normalize "../ip_repo"] [current_project]
update_ip_catalog

# Add source files
add_files -norecurse [file normalize "../top.v"]
add_files -norecurse [file normalize "../j1-universal-16kb-dualport.v"]
add_files -norecurse [file normalize "../uart-fifo.v"]
add_files -norecurse [file normalize "../stack2.v"]
add_files -norecurse [file normalize "../stack3.v"]

# Add constraints file
add_files -fileset constrs_1 -norecurse [file normalize "../pinout.xdc"]

# Add the j1_memory IP
add_files -norecurse [file normalize "../ip_repo/j1_memory/j1_memory.xci"]

# Set top as the top module
set_property top top [current_fileset]
update_compile_order -fileset sources_1

puts "Project created successfully!"
puts "You can now:"
puts "1. Open the project in Vivado GUI"
puts "2. Generate bitstream"
puts "3. Program the Arty-S7-50 board"

exit