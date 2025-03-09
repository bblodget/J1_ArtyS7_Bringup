PROGRAM = base_elided

.PHONY: compile debug clean

compile: $(PROGRAM).hex

debug: $(PROGRAM).asm
	j1asm $< -o $(PROGRAM).hex --symbols --listing --debug

$(PROGRAM).hex: $(PROGRAM).asm
	j1asm $< -o $@ --symbols --listing

clean:
	rm -f $(PROGRAM).sym
	rm -f $(PROGRAM).lst
	rm -f aout.*

cleanall:
	rm -f $(PROGRAM).hex
	rm -f $(PROGRAM).sym
	rm -f $(PROGRAM).lst
	rm -f aout.*
