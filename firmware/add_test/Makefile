BUILD_DIR = build

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/test.hex: test.asm | $(BUILD_DIR)
	j1asm $< > $@

.PHONY: compile clean

compile: $(BUILD_DIR)/test.hex

clean:
	rm -rf $(BUILD_DIR)