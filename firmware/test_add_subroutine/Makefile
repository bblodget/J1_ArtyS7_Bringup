PROGRAM = test_add_subroutine

.PHONY: compile clean

compile: $(PROGRAM).hex

$(PROGRAM).hex: $(PROGRAM).asm
	j1asm $< > $@

clean:
	rm -f $(PROGRAM).hex
