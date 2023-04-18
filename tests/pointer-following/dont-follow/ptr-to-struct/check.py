#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label --all -p f")
expect_no_member_taint("member", output)
expect_no_member_taint("member2", output)

import lldb_dfsan

expect_not(lldb_dfsan.format_label(1), output)
