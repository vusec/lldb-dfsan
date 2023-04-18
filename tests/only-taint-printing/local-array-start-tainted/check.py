#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label i")
expect_member_taint("[0]", 1, output)
expect_not("[1]", output)
expect_not("[2]", output)
