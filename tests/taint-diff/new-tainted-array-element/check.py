#!/usr/bin/env python3

from dfsan_test import *

# No indentation.
output = start_and_run(["label --diff array", "continue", "label --diff array"])

parts = output.split("continue")

# In the first run only the [1] element is displayed.
expect_member_taint("[1]", 1, parts[0])
expect_not("[2]", parts[0])

# [2] is now also tainted, so it should be displayed but not [1]
expect_not("[1]", parts[1])
expect_member_taint("[2]", 1, parts[1])