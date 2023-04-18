#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label --all f")
expect_member_taint("member", 1, output)
expect_no_member_taint("self", output)
expect_member_taint("trailing", 1, output)
