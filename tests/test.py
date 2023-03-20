#!/usr/bin/env python3

import argparse
import os
import subprocess as sp
import tempfile
import shutil
import os.path as path
import sys

tests = []

script_dir = os.path.dirname(os.path.realpath(__file__))
plugin_path = path.join(script_dir, "..", "lldb-dfsan.py")


class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    PASS = BOLD + GREEN
    FAIL = BOLD + RED


parser = argparse.ArgumentParser(prog="test", description="Runs the tests")
parser.add_argument("--verbose", action="store_true", help="Hides verbose output")
args = parser.parse_args()


utils_dir = path.join(script_dir, "test-utils")
main_dir = path.join(script_dir, "..")
pythonpath = utils_dir + ":" + main_dir
if "PYTHONPATH" in os.environ:
    pythonpath += ":" + os.environ["PYTHONPATH"]
os.environ["PYTHONPATH"] = pythonpath
print(os.environ["PYTHONPATH"])

if len(tests) == 0:
    for test in os.listdir(script_dir):
        if os.path.exists(path.join(script_dir, test, "check.py")):
            tests.append(path.join(script_dir, test))


def run_test(directory):
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = path.join(tmpdir, "test")
        shutil.copytree(directory, test_dir)
        output = sp.check_output(
            [path.join(test_dir, "check.py"), plugin_path], cwd=test_dir
        )
        if args.verbose and output:
            print(output)


print("Running {num} tests".format(num=len(tests)))
had_error = False
for test in tests:
    test_name = os.path.basename(test)
    sys.stdout.write("• " + test_name + " ")
    sys.stdout.flush()
    try:
        run_test(test)
    except sp.CalledProcessError as e:
        had_error = True
        print(Color.FAIL + "FAIL" + Color.END)
        if e.stdout:
            print(e.stdout.decode("utf-8"))
        if e.stderr:
            print(e.stderr.decode("utf-8"))
        continue
    sys.stdout.write((30 - len(test_name)) * " ")
    print("[" + Color.PASS + "OK" + Color.END + "]")

if had_error:
    sys.exit(1)