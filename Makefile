EXE_FILE = forvis_exe

# Compiles the Haskell source files in SRC_DIR into the EXE_FILE using
# the ghc Haskell compiler, placing compiler-intermediate files in
# TMP_DIR.

.PHONY: default
default:
	@echo "    make exe           Compile Haskell source files from '$(SRC_DIR)' into Forvis executable."
	@echo "    make test          Run $(EXE_FILE) as a RISC-V simulator on sample ISA test $(SAMPLE_ISA_TEST)."
	@echo "    make test_v1       -- ditto, with verbosity 1 (+ print instruction trace)."
	@echo "    make test_v2       -- ditto, with verbosity 2 (+ print arch state after each instr)."
	@echo "    make test_hello    Run $(EXE_FILE) as a RISC-V simulator on classic 'Hello World!' C program"
	@echo "                           compiled with gcc into a RISC-V ELF binary."
	@echo "    make test_thue     Run $(EXE_FILE) as a RISC-V simulator on compiled Thuemorse C program."

# ================================================================
# Compile Haskell source files from SRC_DIR into Forvis executable
# using the ghc Haskell compiler.
# Compiler-intermediate files are placed in TMP_DIR.

SRC_DIR  = ./src
TMP_DIR  = tmp_haskell

.PHONY: exe
exe:
	mkdir -p  $(TMP_DIR)
	ghc  -o  $(EXE_FILE)  -O2  -i$(SRC_DIR)  -outputdir  $(TMP_DIR)  Main

# ================================================================
# Running a sample ISA test
# (Substitute SAMPLE_ISA_TEST and SAMPLE_ISA_TEST_RV for a different ISA test.)
# (See Regression_Testing/Makefile for running all the ISA tests)

TEST_PROGRAMS      = Test_Programs
SAMPLE_ISA_TEST    = rv64ui-p-add
SAMPLE_ISA_TEST_RV = RV64
N = 100000

.PHONY: test
test: $(EXE_FILE)
	./$(EXE_FILE)  --$(SAMPLE_ISA_TEST_RV)  --n $(N) \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/riscv-tests/isa/$(SAMPLE_ISA_TEST)

.PHONY: test_v1
test_v1: $(EXE_FILE)
	./$(EXE_FILE)  --$(SAMPLE_ISA_TEST_RV)  --n $(N)  --verbosity 1  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/riscv-tests/isa/$(SAMPLE_ISA_TEST)

.PHONY: test_v2
test_v2: $(EXE_FILE)
	./$(EXE_FILE)  --$(SAMPLE_ISA_TEST_RV)  --n $(N)  --verbosity 2  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/riscv-tests/isa/$(SAMPLE_ISA_TEST)

# ================================================================
# Running sample C programs compiled by gcc to ELF files

# Standard C program that prints "Hello World!\n"
.PHONY: test_hello
test_hello: $(EXE_FILE)
	./$(EXE_FILE)  --RV64  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/MIT/rv64-hello

.PHONY: test_hello_v1
test_hello_v1: $(EXE_FILE)
	./$(EXE_FILE)  --RV64  --verbosity 1  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/MIT/rv64-hello

.PHONY: test_hello_v2
test_hello_v2: $(EXE_FILE)
	./$(EXE_FILE)  --RV64  --verbosity 2  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/MIT/rv64-hello

# C program that does some computation and prints out a string of 0s and 1s
.PHONY: test_thue
test_thue: $(EXE_FILE)
	./$(EXE_FILE)  --RV64  \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/MIT/rv64-thuemorse

# Linux kernel
.PHONY: test_linux_boot
test_linux_boot: $(EXE_FILE)
	./$(EXE_FILE)  --RV64  -n 200000000 \
		$(TEST_PROGRAMS)/boot_ROM_RV64.hex32 \
		$(TEST_PROGRAMS)/Linux_kernel/rv64-vmlinux.elf

# ================================================================
# Cleanup

.PHONY: clean
clean:
	rm  -r -f  *~  $(SRC_DIR)/*~  $(TMP_DIR)  *.hi *.o

.PHONY: full_clean
full_clean:
	rm  -r -f  *~  $(SRC_DIR)/*~  $(TMP_DIR)  *.hi *.o  $(EXE_FILE)

# ================================================================
