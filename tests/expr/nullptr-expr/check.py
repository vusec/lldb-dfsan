#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label (int*)(0xffffffffffffffffULL)")
expect("No shadow memory", output)