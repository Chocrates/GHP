from pydbg import *
from pydbg.defines import *

import struct
import random


# This is our user defined callback function
def printf_randomizer(dbg):
    # Read in the value of the counter at ESP + 0x08 as a DWORD
    parameter_addr = dbg.context.Esp + 0x4
    counter = dbg.read_process_memory(parameter_addr, 4)

    # When we use read_process_memory, it returns a packed binary
    # string.  We must first unpack it before we can use it further.
    parameter_base_addr = struct.unpack("L", counter)[0]
    string_len = 15 + 4 + 2  # "Loop iteration " the number then "!\n"
    counter_string = dbg.read_process_memory(parameter_base_addr, int(string_len))
    counter_string = struct.unpack(str(string_len) + "s", counter_string)[0]

    counter_string = counter_string.split("!\n")[0]
    counter = counter_string[15]

    print "Counter: %d" % int(counter)
    # print dbg.dump_context()

    # Generate a random number and pack it into binary format
    # so that it is written correctly back into the process
    random_counter = random.randint(1, 100)
    print "[*] Random count: %d" % random_counter
    random_counter = struct.pack("L", random_counter)[0]


    # Now swap in our random number and resume the process
    dbg.write_process_memory(parameter_addr, random_counter)

    return DBG_CONTINUE


# Instantiate the pydgb class
dbg = pydbg()

# Now enter the PID of the printf_loop.py process
pid = raw_input("Enter the printf_loop.py PID: ")

# Attach the debugger to the proccess
dbg.attach(int(pid))

# Set the breakpoint with the printf_randomizer function
# Defined as a callback
printf_address = dbg.func_resolve("msvcrt", "printf")
print "[*] Printf address: %d" % printf_address
dbg.bp_set(printf_address, description="printf_address", handler=printf_randomizer)

# Resume the process
dbg.run()
