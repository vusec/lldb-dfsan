#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label --all (int*)(0x0ULL)")
expect("No shadow memory", output)
