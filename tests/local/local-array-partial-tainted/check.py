#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label --all i")
expect_member_taint("[0]", 0, output)
expect_member_taint("[1]", 1, output)
expect_member_taint("[2]", 0, output)
