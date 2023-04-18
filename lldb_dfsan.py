#!/usr/bin/env python3

import lldb
import shlex
import optparse

class TaintData:
    def __init__(self,
                 address : int,
                 taint : int):
        self.address = address
        self.taint = taint

taint_storage = {}

def get_label_of_address(frame, addr, store_read = True):
    thread = frame.thread
    process = thread.process
    target = process.target

    # Transform addr to shadow value.
    shadow_addr = addr.GetLoadAddress(target) ^ 0x500000000000
    error = lldb.SBError()
    # Read shadow value from process.
    content = process.ReadMemory(shadow_addr, 1, error)
    if error.Fail():
        print("Failed to read process memory at " + str(shadow_addr))
        print(error)

    # Return read shadow value.
    shadow_value = bytearray(content)[0] # type: int

    if store_read:
        taint_storage[addr.GetLoadAddress(target)] = shadow_value

    return shadow_value


def get_label_of_value(frame, var):
    return get_label_of_address(frame, var.addr)


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


def format_label(label: int):
    if label == 0:
        return "No taint"
    return Color.BOLD + Color.RED + "(Taint class " + str(label) + ")" + Color.END


def print_label(
    result: lldb.SBCommandReturnObject, frame, var: lldb.SBValue, indentation=0
):
    indent = " " * indentation
    type = var.GetType()  # type: lldb.SBType

    result.Print(indent + str(var.name) + " :")
    if type.type == lldb.eTypeClassBuiltin:
        result.Print(" " + format_label(get_label_of_value(frame, var)) + "\n")

    if type.type == lldb.eTypeClassStruct or type.type == lldb.eTypeClassClass:
        result.Print(" struct " + type.name + " {\n")
        for child in var.children:
            print_label(result, frame, child, indentation + 2)
        result.Print(indent + "}\n")

    if type.type == lldb.eTypeClassArray:
        result.Print(" array " + type.name + " {\n")
        for child in var.children:
            print_label(result, frame, child, indentation + 2)
        result.Print(indent + "}\n")


def label(debugger, command, result : lldb.SBCommandReturnObject, dict):
    command_args = shlex.split(command)

    usage = "usage: %prog"
    description = """Print DFSan labels"""
    parser = optparse.OptionParser(description=description, prog="label", usage=usage)
    parser.add_option("-p", "--ptrs",
                  action="store_true", dest="diff", default=False,
                  help="show the taint diff compared to the previous printout")

    label.__doc__ = parser.format_help()

    (options, args) = parser.parse_args(command_args)

    if len(args) == 0:
        print("Not enough arguments")
        return

    target = debugger.GetSelectedTarget()
    if target:
        process = target.GetProcess()
        if process:
            frame = process.GetSelectedThread().GetSelectedFrame() # type: lldb.SBFrame
            if frame:
                expr = " ".join(args)
                var = frame.FindVariable(expr)
                if not var.IsValid():
                    var = frame.EvaluateExpression(expr)
                    if var.error.fail:
                        result.SetError("Could not find variable: " + expr)
                        result.AppendMessage("Expression evaluation failed due to:\n")
                        result.AppendMessage(var.error.description)
                        return
                print_label(result, frame, var)


def __lldb_init_module(debugger, dict):
    debugger.HandleCommand("command script add -f %s.label label" % __name__)
