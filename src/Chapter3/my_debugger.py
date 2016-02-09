from ctypes import *
from my_debugger_defines import *

kernel32 = windll.kernel32

class debugger():
        def __init__(self):
            self.h_process = None
            self.pid = None
            self.debugger_active = False

        def load(self, path_to_exe):
            # dwCreation flag determines how o reate the process
            # set creation_flags = CREATE_NEW_CONSOLE if you want
            # to see the calculator GUI
            creation_flags = DEBUG_PROCESS

            # instantiate the structs
            startupinfo = STARTUPINFO()
            process_information = PROCESS_INFORMATION()

            # The folloing two options allow the started process
            # to be shown as a separate window/  This also illustarates
            # how different settings in the STARTUPINFO struct can affect
            # the debugee
            startupinfo.dwFlags = 0x1
            startupinfo.wShowWindow = 0x0

            # We then initialize the cb variable in the STARTUPINFO struct
            # which is just the size of the struct itself
            startupinfo.cb = sizeof(startupinfo)

            if kernel32.CreateProcessA(path_to_exe,
                                       None,
                                       None,
                                       None,
                                       None,
                                       creation_flags,
                                       None,
                                       None,
                                       byref(startupinfo),
                                       byref(process_information)):
                print "[*] We have successfully launched the process!"
                print "[*] PID: %d" % process_information.dwProcessId

                # Obtain a valid handle to the newly created process
                # and store it for future access
                self.h_process = self.open_process(process_information.dwProcessId)

            else:
                print "[*] Error: 0x%08x." % kernel32.GetLastError()

        def open_process(selfself, pid):
            h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, pid, False)
            return h_process

        def attach(self, pid):
            self.h_process = self.open_process(pid)

            # We attempt to attach to the process
            # if this fails we exit the call
            if kernel32.DebugActiveProcess(pid):
                self.debugger_active = True
                self.pid = int(pid)
                self.run()
            else:
                print "[*] Unable to atach to process."

        def run(self):
            # Now we have to poll the debuggee for debugging events
            while self.debugger_active == True:
                self.get_debug_event()

        def get_debug_event(self):
            debug_event = DEBUG_EVENT()
            continue_status = DBG_CONTINUE

            if kernel32.WaitForDebugEvent(byref(debug_event), INFINITE):
                # Let's obtain the thread and context information
                self.h_thread = self.open_thread(debug_event.dwThreadId)
                self.context = self.get_thread_context(self.h_thread)

                print "Event Code: %d Thread ID: %d" % (debug_event.dwDebugEventCode, debug_event.dwThreadId)

                # If the event is an exception we want to exampine it further
                if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                    # Obtain the exception code
                    exception = debug_event.u.Exception.ExceptionRecord.ExceptionCode
                    self.exception_address = debug_event.u.Exception.ExceptionRecord.ExceptionAddress

                    if exception == EXCEPTION_ACCESS_VIOLATION:
                        print "Access violation detected."
                    # If a breakpoint is detected, we call an internal handler
                    elif exception == EXCEPTION_BREAKPOINT:
                        continue_status = self.exception_handler_breakpoint()
                    elif exception == EXCEPTION_GUARD_PAGE:
                        print "Guard page access detected."
                    elif exception == EXCEPTION_SINGLE_STEP:
                        print "Single step exception detected"

                kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)

        def exception_handler_breakpoint(self):
            print "[*] Inside breakpoint handler."
            print "Exception Address: 0x%08x" % self.exception_address
            return DBG_CONTINUE

        def detach(self):
            if kernel32.DebugActiveProcessStop(self.pid):
                print "[*] Finished Ddebugging. Exiting..."
                return True
            else:
                print "There was an error"
                return False

        def open_thread(self, thread_id):
            h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)

            if h_thread is not None:
                return h_thread
            else:
                print "[*] Could not obtain thread handle"

        def enumerate_threads(self):
            thread_entry = THREADENTRY32()
            thread_list = []

            snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)

            if snapshot is not None:
                # You have tos et the size of the struct or the call will fail
                thread_entry.dwSize = sizeof(thread_entry)
                success = kernel32.Thread32First(snapshot, byref(thread_entry))

                while success:
                    if thread_entry.th32OwnerProcessID == self.pid:
                        thread_list.append(thread_entry.th32ThreadID)

                    success = kernel32.Thread32Next(snapshot, byref(thread_entry))

                kernel32.CloseHandle(snapshot)
                return thread_list
            else:
                return False

        def get_thread_context(self, thread_id):
            context = CONTEXT()
            context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

            # Obtani a handle to the thread
            h_thread = self.open_thread(thread_id)

            if kernel32.GetThreadContext(h_thread, byref(context)):
                kernel32.CloseHandle(h_thread)
                return context
            else:
                return False
