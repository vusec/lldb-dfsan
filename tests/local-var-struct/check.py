#!/usr/bin/env python3

from dfsan_test import *

compile()
output = start_and_run("label f")
expect("member - (Taint class 1)", output)
expect("member2 - No taint", output)