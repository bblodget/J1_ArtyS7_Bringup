VIVADO = vivado
VIVADO_FLAGS = -mode tcl -source

.PHONY: create_project clean

create_project:
	$(VIVADO) $(VIVADO_FLAGS) create_j1_memory.tcl -nolog -nojournal

clean:
	rm -rf j1_memory_edit
	rm -rf .Xil
	rm -f vivado.jou vivado.log
	rm -f *.backup.jou *.backup.log