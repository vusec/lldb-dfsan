#!/usr/bin/env python3

import subprocess as sp
import sys

def compile():
    args = ["clang", "main.c", "-o", "binary", "-fsanitize=dataflow", "-g"]
    print("Running: " + " ".join(args))
    sp.check_call(args)

def start_and_run(cmds):
    if isinstance(cmds, str):
        cmds = [cmds]
    args = ["lldb", "binary", "-b", "-o", "breakpoint set -p STOP", "-o", "run"]
    args += ["-o", "command script import lldb_dfsan"]
    for cmd in cmds:
        args += ["-o"]
        args += [cmd]
    print("Running: " + " ".join(args))
    return sp.check_output(args).decode("utf-8")

class Color:
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"

def clean_output(output):
    output = output.replace(Color.RED, "")
    output = output.replace(Color.END, "")
    output = output.replace(Color.BOLD, "")
    return output

def expect(token, output):
    output = clean_output(output)
    if not token in output:
        print("Failed to find token " + token + " in " + output)
        sys.exit(1)

def expect_not(token, output):
    output = clean_output(output)
    if token in output:
        print("Found unexpected token " + token + " in " + output)
        sys.exit(1)
    