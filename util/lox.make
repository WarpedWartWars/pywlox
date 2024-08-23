# Makefile for building a single configuration of the Loxlox interpreter. It expects
# variables to be passed in for:
#
# MODE         "extended" or "release". (default "release")
# NAME         Name of the output executable (and intermediate file directory).
# SOURCE_DIR   Directory where source files are found.

# Mode configuration.
ifeq ($(MODE),extended)
	LOXFLAGS := -e
	BUILD_DIR := build/extended
else
	LOXFLAGS := 
	BUILD_DIR := build/release
endif

# Files.
SOURCES := $(wildcard $(SOURCE_DIR)/*.lox)
OBJECTS := $(wildcard $(BUILD_DIR)/$(NAME)/*.loxasm)

# Targets ---------------------------------------------------------------------

# Link the interpreter.
build/$(NAME): $(OBJECTS)
	@ printf "%8s %-20s %s\n" $(LOXCMP) $@ "$(LOXFLAGS)"
	@ mkdir -p build
	@ $(LOXCMP) $(LOXFLAGS) $^ -o $@

# Compile object files.
$(BUILD_DIR)/$(NAME)/%.loxasm: $(SOURCE_DIR)/%.lox
	@ printf "%8s %-20s %s\n" $(LOXCMP) $< "$(LOXFLAGS)"
	@ mkdir -p $(BUILD_DIR)/$(NAME)
	@ $(LOXCMP) $(LOXFLAGS) -o $@ $<

.PHONY: default
