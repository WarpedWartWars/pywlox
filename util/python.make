# Makefile for building a single configuration of the pylox interpreter. It expects
# variables to be passed in for:
#
# MODE         "extended" or "release". (default "release")
# NAME         Name of the output executable (and intermediate file directory).
# SOURCE_DIR   Directory where source files are found.

# Mode configuration.
ifeq ($(MODE),extended)
	PYFLAGS := #-e              #TODO: how to set variable at compile-time
	BUILD_DIR := build/extended # (decide on compiler first)
else                            # sounds like a job for macros but
	PYFLAGS :=                  # python it no havey havey them
	BUILD_DIR := build/release
endif

# Files.
SOURCES := $(wildcard $(SOURCE_DIR)/*.py)
#OBJECTS := $(wildcard $(BUILD_DIR)/$(NAME)/*.)

# Targets ---------------------------------------------------------------------

# Link the interpreter.
build/$(NAME): $(OBJECTS)
	@ printf "%8s %-20s %s\n" $(PYCMP) $@ "$(PYFLAGS)"
	@ mkdir -p build
	@ $(PYCMP) $(PYFLAGS) $^ -o $@

# Compile object files.
#$(BUILD_DIR)/$(NAME)/%.loxasm: $(SOURCE_DIR)/%.lox
#	@ printf "%8s %-20s %s\n" $(PYCMP) $< "$(PYFLAGS)"
#	@ mkdir -p $(BUILD_DIR)/$(NAME)
#	@ $(PYCMP) $(PYFLAGS) -o $@ $<

.PHONY: default
