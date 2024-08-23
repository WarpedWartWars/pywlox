from pathlib import Path
import sys
import re

def runFile(path):
    with path.open() as p:
        b=p.read()
    import common
    import vm
    vm.VM().interpret(b)
    common.stdout.seek(0)
    common.stderr.seek(0)
    _to,_te=common.stdout.read(),common.stderr.read()
    common.stdout.close()
    common.stderr.close()
    common.stdout.__init__()
    common.stderr.__init__()
    del common
    del vm
    return _to,_te

expectedOutputPattern       = re.compile(r"// expect: ?(.*)")
expectedErrorPattern        = re.compile(r"// (Error.*)")
errorLinePattern            = re.compile(r"// \[((c|py) )?line (\d+)\] (Error.*)")
expectedRuntimeErrorPattern = re.compile(r"// expect runtime error: (.+)")
syntaxErrorPattern          = re.compile(r"\[.*line (\d+)\] (Error.+)")
stackTracePattern           = re.compile(r"\[line (\d+)\]")
nonTestPattern              = re.compile(r"// nontest")

class Test:
    def __init__(self, path):
        self.path = path
        self.expectedOutput = []
        self.expectedErrors = set()
        self.expectedRuntimeError = None
        self.runtimeErrorLine = 0
        self.failures = []

    def parse(self):
        with path.open() as p:
            lines = p.readlines()
        for ln,lin in enumerate(lines):
            lineNum=ln+1
            line=lin.strip("\r\n")

            global expectations

            mtch = nonTestPattern.search(line)
            if mtch is not None: return False

            mtch = expectedOutputPattern.search(line)
            if mtch is not None:
                self.expectedOutput.append((lineNum, mtch[1]))
                expectations += 1
                continue

            mtch = expectedErrorPattern.search(line)
            if mtch is not None:
                self.expectedErrors.add(f"[{lineNum}] {mtch[1]}")
                expectations += 1
                continue

            mtch = errorLinePattern.search(line)
            if mtch is not None:
                self.expectedErrors.add(f"[{mtch[3]}] {mtch[4]}")
                expectations += 1
                continue

            mtch = expectedRuntimeErrorPattern.search(line)
            if mtch is not None:
                self.runtimeErrorLine = lineNum
                self.expectedRuntimeError = mtch[1]
                expectations += 1

        if len(self.expectedErrors) > 0 and self.expectedRuntimeError is not None:
            print(f"TEST ERROR {self.path}\n     Cannot expect both compile and runtime errors.\n")
            return False

        return True

    def run(self):
        output, error = runFile(self.path)
        outputLines = output.splitlines()
        errorLines = error.splitlines()

        if self.expectedRuntimeError is not None:
            self.validateRuntimeError(errorLines)
        else:
            self.validateCompileErrors(errorLines)

        self.validateOutput(outputLines)
        return self.failures

    def validateRuntimeError(self, errorLines):
        if len(errorLines) < 2:
            self.fail(f"Expected runtime error '{self.expectedRuntimeError}' and got none.")
            return

        if errorLines[0] != self.expectedRuntimeError:
            self.fail(f"Expected runtime error '{expectedRuntimeError}' and got:", errorLines[0])

        mtch = None
        stackLines = errorLines[1:]
        for line in stackLines:
            mtch = stackTracePattern.search(line)
            if mtch is not None: break

        if mtch is None:
            self.fail("Expected stack trace and got:", *stackLines)
        else:
            stackLine = int(mtch[1])
            if stackLine != self.runtimeErrorLine:
                fail(f"Expected runtime error on line {runtimeErrorLine} "
                     f"but was on line {stackLine}.")

    def validateCompileErrors(self, errorLines):
        foundErrors = set()
        unexpectedCount = 0
        for line in errorLines:
            mtch = syntaxErrorPattern.search(line)
            if mtch is not None:
                error = f"[{mtch[1]}] {mtch[2]}"
                if error in self.expectedErrors:
                    foundErrors.add(error)
                else:
                    if unexpectedCount < 10:
                        self.fail("Unexpected error:", line)
                    unexpectedCount += 1
            elif line != "":
                if unexpectedCount < 10:
                    self.fail("Unexpected output on stderr:", line)
                unexpectedCount += 1

        if unexpectedCount > 10:
            self.fail(f"(truncated {unexpectedCount - 10} more...)")

        for error in self.expectedErrors.difference(foundErrors):
            self.fail(f"Missing expected error: {error}")

    def validateOutput(self, outputLines):
        if len(outputLines) > 0 and outputLines[-1] == "":
            outputLines.pop()

        index = 0
        for index in range(len(outputLines)):
            line = outputLines[index]
            if index >= len(self.expectedOutput):
                self.fail(f"Got output '{line}' when none was expected.")
                index += 1
                continue

            expected = self.expectedOutput[index]
            if expected[1] != line:
                self.fail(f"Expected output '{expected[1]}' on line {expected[0]} and got '{line}'.")
        index += 1

        for i in range(index, len(self.expectedOutput)):
            expected = self.expectedOutput[index]
            self.fail(f"Missing expected output '{expected[1]}' on line {expected[0]}.")

    def fail(self, *messages):
        for message in messages:
            self.failures.append(message)

def runTest(path):
    if "test/benchmark" in str(path): return
    if "test/scanning" in str(path): return
    if "test/expressions" in str(path): return

    test = Test(path)

    if not test.parse(): return

    failures = test.run()

    global passed, failed

    if len(failures) == 0:
        passed += 1
    else:
        failed += 1
        print(f"FAIL {path}")
        for failure in failures:
            print(f"     {failure}")
        print()

passed = 0
failed = 0
skipped = 0
expectations = 0

for path in (Path("../test").rglob("*.lox")):
    #print(path)
    runTest(path)

print(f"Passed: {passed} Failed: {failed} Skipped: {skipped}")
if failed == 0:
    print(f"All {passed} tests passed ({expectations} expectations).")
else:
    print(f"{passed} tests passed. {failed} tests failed.")
