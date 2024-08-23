from sys import argv

from common import *
from vm import *

def repl(vm: VM):
    while True:
        line = input("> ")
        if len(line) == 0:
            continue

        try:
            vm.interpret(line)
        except KeyboardInterrupt:
            vm.resetFromBruh()

def readFile(path: str):
    with open(path, "r") as file:
        buffer = file.read()

    return buffer

def runFile(vm: VM, path: str):
    source = readFile(path)
    result = vm.interpret(source)

    if result == INTERPRET.COMPILE_ERROR: exit(65)
    if result == INTERPRET.RUNTIME_ERROR: exit(70)

def main(argc: int, argv: list[str]):
    vm = VM()

    if argc == 1:
        repl(vm)
    elif argc == 2:
        runFile(vm, argv[1])
    else:
        print("Usage: pylox [path]", file=stderr)

if __name__=="__main__":
    try:
        main(len(argv), argv)
    except KeyboardInterrupt:
        print()
