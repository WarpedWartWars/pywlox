default: run_pylox

# Remove all build outputs and intermediate files.
clean:
	@ rm -rf build
	@ rm -rf gen

# Run the tests for the final versions of loxlox and pylox.
test: test_loxlox test_pylox

# Run the tests for the final version of loxlox.
test_loxlox: loxlox
	@ python3 tool/bin/test.py loxlox

# Run the tests for the final version of pylox.
test_pylox: pylox
	@ python3 tool/bin/test.py pylox

# Run the tests for every chapter's version of loxlox.
test_cloxlox: loxlox lox_chapters
	@ python3 tool/bin/test.py loxlox

# Run the tests for every chapter's version of pylox.
test_cpylox: pylox lox_chapters
	@ python3 tool/bin/test.py pylox

# Run the tests for every chapter's versions of loxlox and pylox.
test_all: loxlox pylox lox_chapters compile_snippets
	@ python3 tool/bin/test.py all

# Compile loxlox to one file, because lox doesn't have imports.
impfix:
	@ mkdir -p build
	@ python3 tool/bin/impfix.py lox/main.lox build/loxlox.lox

# Run loxlox with itself.
run_loxlox_loxlox: loxlox
	@ loxlox build/loxlox.lox

# Run loxlox with pylox.
run_loxlox_pylox: loxlox
	@ pylox build/loxlox.lox

# Run pylox.
run_pylox:
	@ python3 python/main.py

# Compile loxlox.
loxlox: impfix
	@ mkdir -p build
	@ $(MAKE) -f util/lox.make NAME=loxlox SOURCE_DIR=lox
	@ cp build/loxlox loxlox # For convenience, copy the interpreter to the top level.

# Compile pylox.
pylox:
	@ mkdir -p build
	@ $(MAKE) -f util/python.make NAME=pylox SOURCE_DIR=python
	@ cp build/pylox pylox # For convenience, copy the interpreter to the top level.

lox_chapters: split_chapters
	@ $(MAKE) -f util/lox.make NAME=chap14_chunks SOURCE_DIR=gen/chap14_chunks
	@ $(MAKE) -f util/lox.make NAME=chap15_virtual SOURCE_DIR=gen/chap15_virtual
	@ $(MAKE) -f util/lox.make NAME=chap16_scanning SOURCE_DIR=gen/chap16_scanning
	@ $(MAKE) -f util/lox.make NAME=chap17_compiling SOURCE_DIR=gen/chap17_compiling
	@ $(MAKE) -f util/lox.make NAME=chap18_types SOURCE_DIR=gen/chap18_types
	@ $(MAKE) -f util/lox.make NAME=chap19_strings SOURCE_DIR=gen/chap19_strings
	@ $(MAKE) -f util/lox.make NAME=chap20_hash SOURCE_DIR=gen/chap20_hash
	@ $(MAKE) -f util/lox.make NAME=chap21_global SOURCE_DIR=gen/chap21_global
	@ $(MAKE) -f util/lox.make NAME=chap22_local SOURCE_DIR=gen/chap22_local
	@ $(MAKE) -f util/lox.make NAME=chap23_jumping SOURCE_DIR=gen/chap23_jumping
	@ $(MAKE) -f util/lox.make NAME=chap24_calls SOURCE_DIR=gen/chap24_calls
	@ $(MAKE) -f util/lox.make NAME=chap25_closures SOURCE_DIR=gen/chap25_closures
	@ $(MAKE) -f util/lox.make NAME=chap26_garbage SOURCE_DIR=gen/chap26_garbage
	@ $(MAKE) -f util/lox.make NAME=chap27_classes SOURCE_DIR=gen/chap27_classes
	@ $(MAKE) -f util/lox.make NAME=chap28_methods SOURCE_DIR=gen/chap28_methods
	@ $(MAKE) -f util/lox.make NAME=chap29_superclasses SOURCE_DIR=gen/chap29_superclasses
	@ $(MAKE) -f util/lox.make NAME=chap30_optimization SOURCE_DIR=gen/chap30_optimization

python_chapters: split_chapters
	@ $(MAKE) -f util/python.make NAME=chap14_chunks SOURCE_DIR=gen/chap14_chunks
	@ $(MAKE) -f util/python.make NAME=chap15_virtual SOURCE_DIR=gen/chap15_virtual
	@ $(MAKE) -f util/python.make NAME=chap16_scanning SOURCE_DIR=gen/chap16_scanning
	@ $(MAKE) -f util/python.make NAME=chap17_compiling SOURCE_DIR=gen/chap17_compiling
	@ $(MAKE) -f util/python.make NAME=chap18_types SOURCE_DIR=gen/chap18_types
	@ $(MAKE) -f util/python.make NAME=chap19_strings SOURCE_DIR=gen/chap19_strings
	@ $(MAKE) -f util/python.make NAME=chap20_hash SOURCE_DIR=gen/chap20_hash
	@ $(MAKE) -f util/python.make NAME=chap21_global SOURCE_DIR=gen/chap21_global
	@ $(MAKE) -f util/python.make NAME=chap22_local SOURCE_DIR=gen/chap22_local
	@ $(MAKE) -f util/python.make NAME=chap23_jumping SOURCE_DIR=gen/chap23_jumping
	@ $(MAKE) -f util/python.make NAME=chap24_calls SOURCE_DIR=gen/chap24_calls
	@ $(MAKE) -f util/python.make NAME=chap25_closures SOURCE_DIR=gen/chap25_closures
	@ $(MAKE) -f util/python.make NAME=chap26_garbage SOURCE_DIR=gen/chap26_garbage
	@ $(MAKE) -f util/python.make NAME=chap27_classes SOURCE_DIR=gen/chap27_classes
	@ $(MAKE) -f util/python.make NAME=chap28_methods SOURCE_DIR=gen/chap28_methods
	@ $(MAKE) -f util/python.make NAME=chap29_superclasses SOURCE_DIR=gen/chap29_superclasses
	@ $(MAKE) -f util/python.make NAME=chap30_optimization SOURCE_DIR=gen/chap30_optimization

diffs: split_chapters
	@ mkdir -p build/diffs
	@ -diff --new-file nonexistent/ gen/chap14_chunks/ > build/diffs/chap14_chunks.diff
	@ -diff --new-file gen/chap14_chunks/ gen/chap15_virtual/ > build/diffs/chap15_virtual.diff
	@ -diff --new-file gen/chap15_virtual/ gen/chap16_scanning/ > build/diffs/chap16_scanning.diff
	@ -diff --new-file gen/chap16_scanning/ gen/chap17_compiling/ > build/diffs/chap17_compiling.diff
	@ -diff --new-file gen/chap17_compiling/ gen/chap18_types/ > build/diffs/chap18_types.diff
	@ -diff --new-file gen/chap18_types/ gen/chap19_strings/ > build/diffs/chap19_strings.diff
	@ -diff --new-file gen/chap19_strings/ gen/chap20_hash/ > build/diffs/chap20_hash.diff
	@ -diff --new-file gen/chap20_hash/ gen/chap21_global/ > build/diffs/chap21_global.diff
	@ -diff --new-file gen/chap21_global/ gen/chap22_local/ > build/diffs/chap22_local.diff
	@ -diff --new-file gen/chap22_local/ gen/chap23_jumping/ > build/diffs/chap23_jumping.diff
	@ -diff --new-file gen/chap23_jumping/ gen/chap24_calls/ > build/diffs/chap24_calls.diff
	@ -diff --new-file gen/chap24_calls/ gen/chap25_closures/ > build/diffs/chap25_closures.diff
	@ -diff --new-file gen/chap25_closures/ gen/chap26_garbage/ > build/diffs/chap26_garbage.diff
	@ -diff --new-file gen/chap26_garbage/ gen/chap27_classes/ > build/diffs/chap27_classes.diff
	@ -diff --new-file gen/chap27_classes/ gen/chap28_methods/ > build/diffs/chap28_methods.diff
	@ -diff --new-file gen/chap28_methods/ gen/chap29_superclasses/ > build/diffs/chap29_superclasses.diff
	@ -diff --new-file gen/chap29_superclasses/ gen/chap30_optimization/ > build/diffs/chap30_optimization.diff

split_chapters:
	@ python3 tool/bin/split_chapters.py

compile_snippets:
	@ python3 tool/bin/compile_snippets.py

.PHONY: lox_chapters python_chapters clean loxlox pylox compile_snippets default diffs split_chapters test test_all test_loxlox test_pylox test_cloxlox test_cpylox run_loxlox_loxlox run_loxlox_pylox run_pylox
