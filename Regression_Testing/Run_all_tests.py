#!/usr/bin/python3

# Copyright (c) 2018 Rishiyur S. Nikhil
# See LICENCE for license details

usage_line = "Usage:    {0}    <root-dir-for-ISA-tests>    <logs_dir>\n"

help_lines = "  Runs a Forvis executable  on each ELF file in <root-dir> and its sub-directories.\n" \
             "  For each source file FOO, saves output log in <logs_dir>/FOO.log. \n"

import sys
import os
import stat
import subprocess

# ================================================================
# Ignores files with the following in their names

ignore_list = [".",                   # Files with extensions (e.g., foo.dump)
               "rv32uc", "rv64uc",    # C (compressed) not yet implemented
               "rv32uf", "rv64uf",    # Single precision floating point not yet implemented
               "rv32ud", "rv64ud"]    # Double precision floating point not yet implemented

# ================================================================

forvis_exe = "../forvis_exe"

num_executed = 0
num_passed   = 0

# ================================================================

def main (argv = None):
    if ((len (argv) <= 1) or
        (argv [1] == '-h') or (argv [1] == '--help') or
        (len (argv) != 3)):
        sys.stdout.write (usage_line.format (argv [0]))
        sys.stdout.write ("\n")
        sys.stdout.write (help_lines)
        sys.stdout.write ("\n")
        return 0

    path      = os.path.abspath (os.path.normpath (argv [1]))
    logs_path = os.path.abspath (os.path.normpath (argv [2]))
    max_level = 20
    traverse (max_level, 0, path, logs_path)

    sys.stdout.write ("Executed: {0} tests\n".format (num_executed))
    sys.stdout.write ("PASS:     {0} tests\n".format (num_passed))

def traverse (max_level, level, path, logs_path):
    st = os.stat (path)
    is_dir = stat.S_ISDIR (st.st_mode)
    is_reg = stat.S_ISREG (st.st_mode)
    do_foreachfile_function (level, is_dir, is_reg, path, logs_path)
    if is_dir and level < max_level:
        for entry in os.listdir (path):
            traverse (max_level, level + 1, path + "/" + entry, logs_path)
    return 0

# ================================================================
# This function is applied to every path in the
# recursive traversal

def do_foreachfile_function (level, is_dir, is_reg, path, logs_path):
    prefix = ""
    for j in range (level): prefix = "  " + prefix

    # directories
    if is_dir:
        print ("%s%d dir %s" % (prefix, level, path))

    # regular files
    elif is_reg:
        dirname  = os.path.dirname (path)
        basename = os.path.basename (path)
        # print ("%s%d %s" % (prefix, level, path))
        do_regular_file_function (level, dirname, basename, logs_path)

    # other files
    else:
        print ("%s%d Unknown file type: %s" % (prefix, level, os.path.basename (path)))

# ================================================================
# For each ELF file, execute it in the Forvis simulator

def do_regular_file_function (level, dirname, basename, logs_path):
    global num_executed
    global num_passed

    # Ignore file if filename has an extension
    for x in ignore_list:
        if basename.find (x) != -1: return

    rv = None
    if basename.find ("32") != -1:
        rv = "--RV32"
    elif basename.find ("64") != -1:
        rv = "--RV64"

    if rv == None: return

    elf_file = os.path.join (dirname, basename)

    # For debugging only
    prefix = ""
    for j in range (level): prefix = "  " + prefix
    # sys.stdout.write ("{0}{1} ACTION:    {2}\n".format (prefix, level, elf_file))

    if (rv == "--RV32"):
        boot_rom_file = "../Test_Programs/boot_ROM_RV32.hex32"
    else:
        boot_rom_file = "../Test_Programs/boot_ROM_RV64.hex32"

    command = [forvis_exe,  rv,  "--tohost",  boot_rom_file,  elf_file]

    sys.stdout.write ("Test {0}\n".format (basename))
    sys.stdout.write ("    Exec:")
    for x in command:
        sys.stdout.write (" {0}".format (x))
    sys.stdout.write ("\n")

    # Run command command as a sub-process
    completed_process = run_command (command)
    num_executed = num_executed + 1
    passed = completed_process.stdout.find ("PASS") != -1
    if passed:
        sys.stdout.write ("    PASS")
        num_passed = num_passed + 1
    else:
        sys.stdout.write ("    FAIL")

    log_filename = os.path.join (logs_path, basename + ".log")
    sys.stdout.write ("      Writing log: {0}.log\n".format (basename))

    fd = open (log_filename, 'w')
    fd.write (completed_process.stdout)
    fd.close ()

    return

# ================================================================
# This is a wrapper around 'subprocess.run' because of an annoying
# incompatible change in moving from Python 3.5 to 3.6

def run_command (command):
    python_minor_version = sys.version_info [1]
    if python_minor_version < 6:
        # Python 3.5 and earlier
        result = subprocess.run (args = command,
                                 bufsize = 0,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.STDOUT,
                                 universal_newlines = True)
    else:
        # Python 3.6 and later
        result = subprocess.run (args = command,
                                 bufsize = 0,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.STDOUT,
                                 encoding='utf-8')
    return result

# ================================================================
# For non-interactive invocations, call main() and use its return value
# as the exit code.
if __name__ == '__main__':
  sys.exit (main (sys.argv))
