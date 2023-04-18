#!/usr/bin/env python3

import subprocess as sp
import sys
import lldb_dfsan
import glob


def compile():
    c_source_files = glob.glob("*.c")
    cpp_source_files = glob.glob("*.cpp")
    compiler = "clang"
    if len(cpp_source_files):
        compiler += "++"

    args = [compiler, "-o", "binary", "-fsanitize=dataflow", "-g"]
    args += c_source_files + cpp_source_files
    print("Running: " + " ".join(args))
    sp.check_call(args)


def start_and_run(cmds):
    compile()

    if isinstance(cmds, str):
        cmds = [cmds]
    args = ["lldb", "binary", "--no-lldbinit",
            "-b", "-o", "breakpoint set -p STOP", "-o", "run"]
    args += ["-o", "command script import lldb_dfsan"]
    for cmd in cmds:
        args += ["-o"]
        args += [cmd]
    print("Running: " + " ".join(args))
    result = sp.run(args, stderr=sp.STDOUT, stdout=sp.PIPE)
    return result.stdout.decode("utf-8")


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
    if token not in output:
        raise AssertionError("Failed to find token " + token + " in " + output)


def expect_not(token, output):
    if token in output:
        raise AssertionError("Failed to find token " + token + " in " + output)


def expect_member_taint(member_name, lbl, output):
    expect(member_name + " : " + lldb_dfsan.format_label(lbl), output)

def expect_no_member_taint(member_name, output):
    expect(member_name + " : " + lldb_dfsan.format_label(0), output)

def expect_no_shadow_mem(member_name,output):
    expect(member_name + " : " + lldb_dfsan.format_label(None), output)
