#!/usr/bin/env python3

import lldb
import shlex
import optparse
import sys

def get_label_of_address(frame, addr):
    thread = frame.thread
    process = thread.process
    target = process.target

    # Transform addr to shadow value.
    shadow_addr = addr.GetLoadAddress(target) ^ 0x500000000000
    error = lldb.SBError();
    # Read shadow value from process.
    content = process.ReadMemory(shadow_addr, 1, error)
    if error.Fail():
        print("Failed to read process memory at " + str(shadow_addr))
        print(error)

    # Return read shadow value.
    new_bytes = bytearray(content)
    return new_bytes[0]

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


def format_label(label):
   if label == 0:
      return "No taint"
   return Color.BOLD + Color.RED + "(Taint class " + str(label) + ")" + Color.END

def print_label(frame, var : lldb.SBValue, indentation = 0):
   type = var.GetType() # type: lldb.SBType
   if type.type == lldb.eTypeClassBuiltin:
      sys.stdout.write(" " * indentation + str(var.name))
      print(" - " + format_label(get_label_of_value(frame, var)))
   if type.type == lldb.eTypeClassStruct or type.type == lldb.eTypeClassClass:
      print("struct " + type.name + " {")
      for child in var.children:
         print_label(frame, child, indentation + 2)
      print("}")

def label(debugger, command, result, dict):

  command_args = shlex.split(command)

  usage = "usage: %prog"
  description='''Print DFSan labels'''
  parser = optparse.OptionParser(description=description, prog='label', usage=usage)
  label.__doc__ = parser.format_help()

  try:
      (options, args) = parser.parse_args(command_args)
  except:
      return
  
  if len(args) == 0:
    print("Not enough arguments")
    return

  target = debugger.GetSelectedTarget()
  if target:
    process = target.GetProcess()
    if process:
      frame = process.GetSelectedThread().GetSelectedFrame()
      if frame:
        var = frame.FindVariable(args[0])
        print_label(frame, var)

def __lldb_init_module (debugger, dict):
  debugger.HandleCommand('command script add -f %s.label label' % __name__)