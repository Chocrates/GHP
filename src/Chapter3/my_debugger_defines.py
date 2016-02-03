from ctypes import *

# Map MS types to cyptes
WORD = c_ushort
DWORD = c_ulong
LPBYTE = POINTER(c_ubyte)
LPSTR = POINTER(c_char)
HANDLE = c_void_p

# constants
DEUBG_PROCESS = 0x00000001
CREATE_NEW_CONSOLE = 0x00000010

# structs for CreateProcessA()
class STARTUPINFO(Structure):
    _fields_ = [
        ("cb", DWORD),
        ("lpReserved", LPSTR),
        ("lpDesktop", LPSTR),
        ("lpTitle", LPSTR),
        ("dwX", DWORD),
        ("dwY", DWORD),
        ("dwXSize", DWORD),
        ("dwYSize", DWORD),
        ("dwXCountChars", DWORD),
        ("dwYCountChars", DWORD),
        ("dwFillAttribute", DWORD),
        ("dwFlags", DWORD),
        ("wShowWindow", DWORD),
        ("cbReserved2", DWORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", HANDLE),
        ("hStdOutput", HANDLE),
        ("hStdError", HANDLE),
    ]

class PROCESS_INFORMATION(Structure):
        _fields_ = [
            ("hProcess", HANDLE),
            ("hThread", HANDLE),
            ("dwProcessId", DWORD),
            ("dwThreadId", DWORD)
        ]