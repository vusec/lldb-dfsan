#!/usr/bin/env python3

from dfsan_test import *

compile()
output = start_and_run("label i")
expect("Taint class 1", output)