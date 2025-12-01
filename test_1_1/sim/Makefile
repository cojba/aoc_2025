# Makefile for safe_dial cocotb testbench

# Simulator configuration
SIM = questa-compat
TOPLEVEL_LANG = verilog

# Project paths
RTL_DIR = ../rtl

# RTL source files
VERILOG_SOURCES = $(RTL_DIR)/safe_dial.sv

# DUT parameters
DIAL_SIZE ?= 100
CLK_PERIOD_NS ?= 10

# Export parameters as environment variables for Python testbench
export DIAL_SIZE
export CLK_PERIOD_NS

# Toplevel module
TOPLEVEL = safe_dial

# Python test module
MODULE = test_safe_dial

# QuestaSim specific settings
# Enable waveform generation and full visibility

# Use the patched cocotb environment
COCOTB_MAKEFILES = /home/ubuntu/.cache/pypoetry/virtualenvs/asd-IvK9WrkW-py3.12/lib/python3.12/site-packages/cocotb_tools/makefiles

# Include cocotb makefiles
include $(COCOTB_MAKEFILES)/Makefile.sim

# Clean target
clean::
	rm -rf __pycache__ .pytest_cache
	rm -rf sim_build results.xml
	rm -rf transcript vsim.wlf work modelsim.ini
