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

BIT_FILE = $(BUILD_DIR)/j1_base.bit
MMI_FILE = $(BUILD_DIR)/j1_base.mmi

BIT_UPDATED = $(BUILD_DIR)/$(PROJ_NAME).bit

.PHONY: all clean program

all: $(BIT_UPDATED)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Copy base bitstream to build directory
$(BIT_FILE): | $(BUILD_DIR)
	cp $(BASE_BITSTREAM) $(BIT_FILE)

# Copy base MMI to build directory
$(MMI_FILE): | $(BUILD_DIR)
	cp $(BASE_MMI) $(MMI_FILE)

# Assemble the source file using j1asm
$(HEX_FILE): $(PROJ_NAME).asm | $(BUILD_DIR)
	j1asm $< > $@

# Convert HEX to MIF format using hex2mif tool
$(MIF_FILE): $(HEX_FILE)
	@echo "Converting HEX to MIF format..."
	hex2mif $< > $@

# Convert MIF to MEM format
$(MEM_FILE): $(MIF_FILE)
	@echo "Converting MIF to MEM format..."
	mif2mem $< > $@

# Update bitstream with new memory contents
$(BIT_UPDATED): $(MEM_FILE) $(BIT_FILE) $(MMI_FILE)
	@echo "Updating bitstream with new memory contents..."
	updatemem --meminfo $(MMI_FILE) \
		--data $(MEM_FILE) \
		--bit $(BIT_FILE) \
		--proc my_bram \
		--out $(BIT_UPDATED) \
		--force

# Program the FPGA
program: $(BIT_UPDATED)
	$(VIVADO) -mode batch -nolog -nojournal -source program_fpga.tcl \
		-tclargs $(BIT_UPDATED) $(CABLE)

clean:
	rm -rf $(BUILD_DIR)