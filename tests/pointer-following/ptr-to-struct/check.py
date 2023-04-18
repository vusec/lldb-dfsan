#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label f")
expect_no_member_taint("member", output)
expect_no_member_taint("member2", output)
expect_member_taint("nested", 1, output)
