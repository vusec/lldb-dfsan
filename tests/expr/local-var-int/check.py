#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label i,i")
expect("Taint class 1", output)
