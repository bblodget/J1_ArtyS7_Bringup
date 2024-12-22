# Vivado settings
VIVADO = vivado
VIVADO_BATCH = $(VIVADO) -mode batch -source

# Directories
TB_DIR = .
SRC_DIR = ..

# Source files
SOURCES = $(SRC_DIR)/j1-universal-16kb-dualport.v \
          $(SRC_DIR)/stack2.v \
          $(SRC_DIR)/stack3.v \
          $(TB_DIR)/j1_tb.v

# Simulation targets
.PHONY: sim clean

# Default target
all: sim

# Run simulation
sim: $(SOURCES)
	$(VIVADO_BATCH) run_j1_tb.tcl

# Clean up simulation files
clean:
	rm -rf j1_sim
	rm -rf .Xil
	rm -rf *.jou
	rm -rf *.log
	rm -rf *.pb
	rm -rf *.wdb

# Help target
help:
	@echo "Makefile for J1 Processor Testbench"
	@echo ""
	@echo "Targets:"
	@echo "  sim    - Run simulation"
	@echo "  clean  - Remove generated files"
	@echo "  help   - Show this help message"