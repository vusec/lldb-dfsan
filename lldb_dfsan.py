#!/usr/bin/env python3

import lldb
import shlex
import optparse


class TaintData:
    def __init__(self, address: int, taint: int):
        self.address = address
        self.taint = taint

old_taint_storage = {}
taint_storage = {}

def get_previous_taint(addr : int):
    if addr in old_taint_storage:
        return old_taint_storage[addr]
    return None



def get_label_of_address(frame, addr, store_read=True):
    thread = frame.thread
    process = thread.process
    target = process.target

    load_addr = addr.GetLoadAddress(target) # type: int

    # Avoid finding taint by accident on nullptrs.
    if load_addr == 0:
        return None

    # Transform addr to shadow value.
    shadow_addr = load_addr ^ 0x500000000000

    # Read shadow value from process.
    error = lldb.SBError()
    content = process.ReadMemory(shadow_addr, 1, error)
    if error.Fail():
        return None

    # Return read shadow value.
    shadow_value = bytearray(content)[0]  # type: int

    if store_read:
        taint_storage[load_addr] = shadow_value

    return shadow_value


def get_label_of_value(frame, var):
    return get_label_of_address(frame, var.addr)


def format_label(label: int):
    if label is None:
        return "No shadow memory"
    if label == 0:
        return "No taint"
    return Color.BOLD + Color.RED + "(Taint class " + str(label) + ")" + Color.END


class LabelOutput:
    def __init__(self, frame, only_tainted, follow_pointers, indentation, diff):
        self.result = ""
        self.only_tainted = only_tainted
        self.follow_pointers = follow_pointers
        self.indentation_change = indentation
        self.diff = diff

        self.delayed_scopes = []
        self.indentation = 0
        self.seen_addrs = set()
        thread = frame.thread
        process = thread.process
        self.target = process.target

    def start_scope(self, struct_name):
        # Append the struct for now so we can print it on demand later.
        self.delayed_scopes.append(struct_name)

    def end_scope(self):
        if len(self.delayed_scopes) != 0:
            self.delayed_scopes.pop()
        else:
            self.indentation -= self.indentation_change

    def emit_delayed_scopes(self):
        for scope in self.delayed_scopes:
            self.print(scope + "\n")
            self.indentation += self.indentation_change
        self.delayed_scopes = []

    def print_member(self, var : lldb.SBValue, label):
        addr = var.addr.GetLoadAddress(self.target)
        if self.diff:
            old_label = get_previous_taint(addr)
            if old_label == label:
                return
        
        if self.only_tainted and (label is None or label == 0):
            return
        
        member_name = var.name
        self.emit_delayed_scopes()
        self.print(member_name + " : " + format_label(label) + "\n")

    def print(self, s: str):
        self.result += " " * self.indentation
        self.result += s

    def get_final_output(self):
        if len(self.result) == 0:
            return "No tainted memory found"
        return self.result
    
    def _value_to_unique_addr(self, val : lldb.SBValue):
        load_addr = val.addr.GetLoadAddress(self.target)
        return str(load_addr) + " " + str(val.type)

    def printed_value(self, val : lldb.SBValue):
        self.seen_addrs.add(self._value_to_unique_addr(val))

    def should_print_value(self, val : lldb.SBValue):
        load_addr = self._value_to_unique_addr(val)

        if load_addr in self.seen_addrs:
            return False
        return True


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


def print_label(result: LabelOutput, frame, var: lldb.SBValue, indentation=0):
    indent = " " * indentation
    type = var.GetType()  # type: lldb.SBType

    if not result.should_print_value(var):
        return
    result.printed_value(var)

    if type.type == lldb.eTypeClassBuiltin:
        result.print_member(var, get_label_of_value(frame, var))

    elif type.type == lldb.eTypeClassTypedef:
        result.print_member(var, get_label_of_value(frame, var))

    elif type.type == lldb.eTypeClassStruct or type.type == lldb.eTypeClassClass:
        result.start_scope("struct " + type.name)
        for child in var.children:
            print_label(result, frame, child, indentation + 2)
        result.end_scope()

    elif type.type == lldb.eTypeClassArray:
        result.start_scope(var.name + " : " + type.name)
        for child in var.children:
            print_label(result, frame, child, indentation + 2)
        result.end_scope()

    elif type.type == lldb.eTypeClassPointer:
        result.print_member(var, get_label_of_value(frame, var))
        if result.follow_pointers:
            print_label(result, frame, var.deref, indentation + 2)
    else:
        result.print("Unknown type: " + str(type))



def label(debugger, command, result: lldb.SBCommandReturnObject, dict):
    command_args = shlex.split(command)

    usage = "usage: %prog"
    description = """Print DFSan labels"""
    parser = optparse.OptionParser(description=description, prog="label", usage=usage)
    parser.add_option(
        "-p",
        "--no-follow-ptr",
        action="store_false",
        dest="follow_pointers",
        default=True,
        help="Follow pointers when printing taint",
    )

    parser.add_option(
        "-i",
        "--indent",
        action="store",
        type="int",
        dest="indentation",
        default=0,
        help="Indentation in spaces for nested values",
    )

    parser.add_option(
        "-a",
        "--all",
        action="store_false",
        dest="only_tainted",
        default=True,
        help="show only tainted members",
    )

    parser.add_option(
        "-d",
        "--diff",
        action="store_true",
        dest="diff",
        default=False,
        help="Show only taint that changed compared to the last invocation",
    )

    label.__doc__ = parser.format_help()

    (options, args) = parser.parse_args(command_args)

    if len(args) == 0:
        print("Not enough arguments")
        return

    target = debugger.GetSelectedTarget()
    if target:
        process = target.GetProcess()
        if process:
            frame = process.GetSelectedThread().GetSelectedFrame()  # type: lldb.SBFrame
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
                global old_taint_storage
                old_taint_storage = taint_storage.copy()
                output = LabelOutput(frame=frame,
                                     only_tainted=options.only_tainted,
                                     follow_pointers=options.follow_pointers,
                                     indentation=options.indentation,
                                     diff=options.diff)
                print_label(output, frame, var)
                result.Print(output.get_final_output())


def __lldb_init_module(debugger, dict):
    debugger.HandleCommand("command script add -f %s.label label" % __name__)
