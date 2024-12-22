# Set project directory and name
set proj_dir [file normalize "."]
set proj_name "j1_memory_edit"

# Create project
create_project ${proj_name} ${proj_dir}/${proj_name} -part xc7s50csga324-1

# Set project properties
set_property target_language Verilog [current_project]

# Set IP repository paths
set_property ip_repo_paths [file normalize "../ip_repo"] [current_project]
update_ip_catalog

# Add the J1 processor source
add_files -norecurse [file normalize "../j1-universal-16kb-dualport.v"]
add_files -norecurse [file normalize "../stack2.v"]
add_files -norecurse [file normalize "../stack3.v"]

# Set j1 as top module
set_property top j1 [current_fileset]

# Add the existing j1_memory IP
add_files -norecurse [file normalize "../ip_repo/j1_memory/j1_memory.xci"]
update_compile_order -fileset sources_1

puts "Project created successfully. To edit the memory initialization:"
puts "1. Open the project in Vivado GUI"
puts "2. Click on the IP in the Sources window"
puts "3. Click 'Customize IP' in the IP Sources Properties window"
puts "4. Update the COE file path if needed"
puts "5. Click OK and regenerate the IP"

exit