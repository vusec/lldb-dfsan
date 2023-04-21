#!/usr/bin/env python3

from dfsan_test import *

# No indentation.
output = start_and_run("label -i 0 i")
expect("\n[1]", output)

# Print with one space indentation.
output = start_and_run("label -i 1 i")
expect("\n [1]", output)

# Print with two spaces indentation.
output = start_and_run("label -i 2 i")
expect("\n  [1]", output)