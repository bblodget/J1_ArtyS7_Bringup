# Configuration
VIVADO = vivado
PROJ_ROOT = ../..
PROJ_NAME = uart_echo
BASE_BITSTREAM = $(PROJ_ROOT)/bitstream/j1_base.bit
BASE_MMI = $(PROJ_ROOT)/bitstream/j1_base.mmi
CABLE = digilent_arty

# Output directories and files
BUILD_DIR = build
HEX_FILE = $(BUILD_DIR)/$(PROJ_NAME).hex
MIF_FILE = $(BUILD_DIR)/$(PROJ_NAME).mif
MEM_FILE = $(BUILD_DIR)/$(PROJ_NAME).mem
COE_FILE = $(BUILD_DIR)/$(PROJ_NAME).coe

BIT_FILE = $(BUILD_DIR)/j1_base.bit
MMI_FILE = $(BUILD_DIR)/j1_base.mmi

BIT_UPDATED = $(BUILD_DIR)/$(PROJ_NAME).bit

.PHONY: all clean compile bram program

all: compile bram

compile: $(MEM_FILE) $(COE_FILE)

bram: $(BIT_UPDATED)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Copy base bitstream to build directory
$(BIT_FILE): | $(BUILD_DIR)
	cp $(BASE_BITSTREAM) $(BIT_FILE)

# Copy base MMI to build directory
$(MMI_FILE): | $(BUILD_DIR)
	cp $(BASE_MMI) $(MMI_FILE)

# Compile target dependencies
$(HEX_FILE): $(PROJ_NAME).asm | $(BUILD_DIR)
	j1asm $< > $@

$(MIF_FILE): $(HEX_FILE)
	@echo "Converting HEX to MIF format..."
	hex2mif $< > $@

$(MEM_FILE): $(MIF_FILE)
	@echo "Converting MIF to MEM format..."
	mif2mem $< > $@

$(COE_FILE): $(HEX_FILE)
	@echo "Converting HEX to COE format..."
	hex2coe $< > $@

# BRAM update target
$(BIT_UPDATED): $(MEM_FILE) $(BIT_FILE) $(MMI_FILE)
	@echo "Updating bitstream with new memory contents..."
	updatemem --meminfo $(MMI_FILE) \
		--data $(MEM_FILE) \
		--bit $(BIT_FILE) \
		--proc my_bram \
		--out $(BIT_UPDATED) \
		--force

# Program target
program: $(BIT_UPDATED)
	$(VIVADO) -mode batch -nolog -nojournal -source program_fpga.tcl \
		-tclargs $(BIT_UPDATED) $(CABLE)

clean:
	rm -rf $(BUILD_DIR)
	rm -rf *.log
	rm -rf *.jou
	rm -rf *.*.log
	rm -rf *.*.jou