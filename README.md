# lldb-dfsan ![status badge](https://github.com/vusec/lldb-dfsan/actions/workflows/tests.yml/badge.svg)


`lldb-dfsan` is an LLDB plugin that allows inspecting the DFSan labels of
variables, structures and memory in the target process.

## Installation

```bash
pip install lldb-dfsan && echo "command script import lldb_dfsan" >> ~/.lldbinit
```

## How to use

This plugin provides the `label VAR` command which prints all labels of the
references local variable `VAR`. For example:

```bash
Process 38271 stopped
   4    int i[3] = {1, 2, 3};
   5   
   6    dfsan_label i_label = 1;
   7    dfsan_set_label(i_label, &(i[1]), sizeof(int));
(lldb) label i
i : array int[3] {
  [0] : No taint
  [1] : (Taint class 1)
  [2] : No taint
}
```