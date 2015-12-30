from ctypes import *

def printMe():
        print "stuff and things?"

def useCTYPES():
        msvcrt = cdll.msvcrt
        message_string = "Hello world!\n"
        msvcrt.printf("Testing: %s",message_string)

if __name__ == "__main__":
        printMe()
        useCTYPES()