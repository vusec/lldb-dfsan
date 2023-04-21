#!/usr/bin/env python3

from dfsan_test import *

# No indentation by default.
output = start_and_run("label i")
expect("\n[1]", output)