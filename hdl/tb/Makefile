# Vivado settings
VIVADO = vivado
VIVADO_BATCH = $(VIVADO) -mode batch -source

# Directories
TB_DIR = .
SRC_DIR = ..

# Source files
COMMON_SOURCES = $(SRC_DIR)/j1-universal-16kb-dualport.v \
                $(SRC_DIR)/stack2.v \
                $(SRC_DIR)/stack3.v

# Testbench files
J1_TB = $(TB_DIR)/j1_tb.v
J1_UART_TB = $(TB_DIR)/j1_uart_tb.v

# Simulation targets
.PHONY: sim sim_uart clean all

# Default target
all: sim sim_uart

# Run original J1 simulation
sim: $(COMMON_SOURCES) $(J1_TB)
	$(VIVADO_BATCH) run_j1_tb.tcl

# Run UART simulation
sim_uart: $(COMMON_SOURCES) $(J1_UART_TB)
	$(VIVADO_BATCH) run_j1_uart_tb.tcl

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
	@echo "  sim       - Run original simulation"
	@echo "  sim_uart  - Run UART simulation"
	@echo "  all       - Run both simulations"
	@echo "  clean     - Remove generated files"
	@echo "  help      - Show this help message"