# Test Programs
PROGRAMS = test_alu test_compare test_dup_over test_elided test_io test_rstack test_status

# Common settings
ASM = j1asm
ASM_FLAGS = --symbols --listing

.PHONY: all clean $(PROGRAMS)

all: $(PROGRAMS)

# Generic rule for building test programs
$(PROGRAMS): %: %.hex

%.hex: %.asm
	$(ASM) $< -o $@ $(ASM_FLAGS)

# Debug target for any program
debug-%: %.asm
	$(ASM) $< -o $(basename $<).hex $(ASM_FLAGS) --debug

clean:
	rm -f *.hex
	rm -f *.sym
	rm -f *.lst
	rm -f aout.*

# Individual program targets (for explicit building)
test_alu: test_alu.hex
test_compare: test_compare.hex
test_dup_over: test_dup_over.hex
test_elided: test_elided.hex
test_io: test_io.hex
test_rstack: test_rstack.hex
test_status: test_status.hex