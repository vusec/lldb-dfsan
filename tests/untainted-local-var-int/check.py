#!/usr/bin/env python3

from dfsan_test import *

compile()
output = start_and_run("label i")
expect_not("Taint class", output)