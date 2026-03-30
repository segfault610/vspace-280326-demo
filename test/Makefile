SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../src/project.v
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb
MODULE = test
include $(shell cocotb-config --makefiles)/Makefile.sim
