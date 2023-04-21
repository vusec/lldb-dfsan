#!/usr/bin/env python3

from dfsan_test import *

# No indentation.
output = start_and_run(["label --diff array", "continue", "label --diff array"])

parts = output.split("continue")

expect_member_taint("[1]", 1, parts[0])
expect_not("[1]", parts[1])