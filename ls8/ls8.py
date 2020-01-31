#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) <2:
    print("Error, no program specified")
    exit()
program_name = sys.argv[1]
cpu = CPU()

cpu.load(program_name)
cpu.run()