# Get command line arguments
set base_bitstream [lindex $argv 0]
set mif_file [lindex $argv 1]
set output_bitstream [lindex $argv 2]

# Create a temporary project
create_project -in_memory -part xc7s50csga324-1

# Add the base bitstream design
read_bitstream $base_bitstream

# Update the memory initialization
set_property MEMORY_INIT_FILE $mif_file [get_cells -hierarchical -filter {PRIMITIVE_TYPE =~ BMEM.*.*.* }]
refresh_design

# Write new bitstream
write_bitstream -force $output_bitstream

# Cleanup
close_project

exit