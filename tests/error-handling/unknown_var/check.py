#!/usr/bin/env python3

from dfsan_test import *

output = start_and_run("label does_not_exist")
expect("Could not find variable: does_not_exist", output)
