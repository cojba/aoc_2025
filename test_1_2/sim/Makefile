# Makefile for safe_dial_v2 cocotb testbench

# Simulator configuration
SIM ?= questa-compat
TOPLEVEL_LANG ?= verilog

# QuestaSim setup
export SALT_LICENSE_SERVER = 29000@172.31.40.95
export PATH := /home/ubuntu/questasim/linux_aarch64:$(PATH)

# Project paths
RTL_DIR = ../rtl

# RTL source files
VERILOG_SOURCES = $(RTL_DIR)/safe_dial_v2.sv $(RTL_DIR)/mod_barrett.sv

# DUT parameters
DIAL_SIZE ?= 100
CLK_PERIOD_NS ?= 10

# Export parameters as environment variables for Python testbench
export DIAL_SIZE
export CLK_PERIOD_NS

# Toplevel module
TOPLEVEL = safe_dial_v2

# Python test module
MODULE = test_safe_dial_v2

# Waveform dump
WAVES ?= 1

# Use the patched cocotb environment
COCOTB_MAKEFILES = /home/ubuntu/.cache/pypoetry/virtualenvs/asd-IvK9WrkW-py3.12/lib/python3.12/site-packages/cocotb_tools/makefiles

# Include cocotb makefiles
include $(COCOTB_MAKEFILES)/Makefile.sim

# Clean target
clean::
	rm -rf __pycache__ .pytest_cache
	rm -rf sim_build results.xml
	rm -rf transcript vsim.wlf work modelsim.ini
