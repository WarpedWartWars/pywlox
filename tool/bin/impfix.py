import re
from pathlib import Path

_includePattern = re.compile("//include (.+)")

def _addIncludes(inpath, cache):
    if inpath in cache:
        inf = cache[inpath]
    else:
        with open(inpath) as f:
            inf = f.read()
        cache[inpath] = inf
    includes = []
    for line in inf.splitlines():
        match = _includePattern.search(line)
        if match and match[1] not in cache:
            includes += _addIncludes(str(Path(inpath).parent/match[1]), cache)
    includes.append((Path(inpath).name,inf))
    return includes

def main(inpath, outpath):
    includes = _addIncludes(inpath, {})
    with open(outpath, "w") as o:
        for inc in includes:
            o.write("//////// file: %s\n" % inc[0])
            o.write(inc[1])
            o.write("\n")

if __name__=="__main__":
    import sys
    main(*sys.argv[1:3])
