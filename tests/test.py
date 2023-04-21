#!/usr/bin/env python3

import argparse
import os
import subprocess as sp
import tempfile
import shutil
import os.path as path
import sys
from pathlib import Path

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
    WARN = BOLD + YELLOW
    FAIL = BOLD + RED


parser = argparse.ArgumentParser(prog="test", description="Runs the tests")
parser.add_argument("--verbose", action="store_true", dest="verbose", help="Enbles verbose output")
parser.add_argument("-f", "--filter", action="store", dest="filter", default="", help="Filter tests")
args = parser.parse_args()


utils_dir = path.join(script_dir, "test-utils")
main_dir = path.join(script_dir, "..")
pythonpath = utils_dir + ":" + main_dir
if "PYTHONPATH" in os.environ:
    pythonpath += ":" + os.environ["PYTHONPATH"]
os.environ["PYTHONPATH"] = pythonpath

if len(tests) == 0:
    for p in Path(script_dir).rglob("**/check.py"):
        tests.append(str(p.parent))


def run_test(directory):
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = path.join(tmpdir, "test")
        shutil.copytree(directory, test_dir)
        output = sp.check_output(
            [path.join(test_dir, "check.py"), plugin_path], cwd=test_dir
        )
        if args.verbose and output:
            print(output)

separator = Color.BLUE + Color.BOLD + "⇉" + Color.END

print("Running {num} tests".format(num=len(tests)))
had_error = False
for test in tests:
    test_name = str(Path(test).relative_to(script_dir))
    fancy_test_name = test_name.replace("/", separator)
    sys.stdout.write("• ")
    sys.stdout.write(fancy_test_name + " ")
    sys.stdout.flush()


    status = ""
    if args.filter in test_name:
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
        status = Color.PASS + " ✔" + status + Color.END
    else:
        status = Color.WARN + " Skipped" + Color.END
    max_test_len_name = 50
    sys.stdout.write((max_test_len_name - len(test_name)) * "┄")
    print(status)

if had_error:
    sys.exit(1)
