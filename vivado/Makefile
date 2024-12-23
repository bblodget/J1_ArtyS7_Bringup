VIVADO = vivado
VIVADO_FLAGS = -mode tcl -source

.PHONY: create_project clean memory top

# Create memory editing project
memory:
	$(VIVADO) $(VIVADO_FLAGS) create_j1_memory.tcl -nolog -nojournal

# Create implementation project
top:
	$(VIVADO) $(VIVADO_FLAGS) create_top.tcl -nolog -nojournal

clean:
	rm -rf j1_memory_edit
	rm -rf j1_top
	rm -rf .Xil
	rm -f vivado.jou vivado.log
	rm -f *.backup.jou *.backup.log