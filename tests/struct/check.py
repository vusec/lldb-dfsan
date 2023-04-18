#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label f")
expect("struct Foo", output)
expect_member_taint("member", 1, output)
expect_member_taint("member2", 0, output)
