#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label --all &i")
expect_no_shadow_mem("$0", output)
expect_member_taint("*$0", "1", output)
