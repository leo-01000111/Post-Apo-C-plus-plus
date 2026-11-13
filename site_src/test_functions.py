#!/usr/bin/env python3
"""Compile-check every example in functions.py (C++17, g++).

Usage: python site_src/test_functions.py
Env:   CXX = compiler (default g++)
Exit code 0 only if every example compiles. Nothing is ever executed.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from functions import FUNCTIONS  # noqa: E402

FLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Wno-unused-variable",
         "-Wno-unused-but-set-variable", "-Wno-unused-result", "-c"]

# Extra headers some examples need beyond the ones named in `header`.
EXTRA = {"<iostream>"}
FORBIDDEN = re.compile(r"<bits/")


def collect_headers():
    hs = set(EXTRA)
    for f in FUNCTIONS:
        hs.update(re.findall(r"<[^>]+>", f["header"]))
    bad = [h for h in hs if FORBIDDEN.match(h)]
    if bad:
        sys.exit("forbidden headers: %s" % bad)
    return sorted(hs)


def build_source(entries, headers):
    out = ["#include " + h for h in headers]
    for i, f in enumerate(entries):
        out.append("void ex_%d() {  // %s / %s" % (f["_idx"], f["scope"], f["name"]))
        out.append(f["ex"])
        out.append("}")
    out.append("int main() { return 0; }")   # examples are never called
    return "\n".join(out) + "\n"


def compile_src(cxx, src, workdir, tag):
    path = os.path.join(workdir, tag + ".cpp")
    with open(path, "w", encoding="ascii", errors="strict", newline="\n") as fh:
        fh.write(src)
    r = subprocess.run([cxx] + FLAGS + [path, "-o", os.path.join(workdir, tag + ".o")],
                       capture_output=True, text=True)
    return r.returncode, r.stderr


def first_error(stderr):
    for line in stderr.splitlines():
        if "error" in line:
            return line.strip()
    lines = [l for l in stderr.splitlines() if l.strip()]
    return lines[0].strip() if lines else "(no compiler output)"


def main():
    cxx = os.environ.get("CXX") or "g++"
    if shutil.which(cxx) is None:
        sys.exit("compiler not found: %s (set CXX or fix PATH)" % cxx)

    entries = []
    for i, f in enumerate(FUNCTIONS):
        g = dict(f)
        g["_idx"] = i
        entries.append(g)

    required = ("name", "scope", "header", "sig", "ex", "cx", "note")
    problems = 0
    for f in entries:
        for k in required:
            if k not in f:
                print("MISSING FIELD %s in entry %d (%s)" % (k, f["_idx"], f.get("name")))
                problems += 1
        for k in required:
            v = f.get(k, "")
            if not isinstance(v, str) or not v.isascii():
                print("NON-ASCII/NON-STR %s in entry %d (%s)" % (k, f["_idx"], f.get("name")))
                problems += 1
        if "using namespace" in f.get("ex", ""):
            print("using namespace in entry %d (%s)" % (f["_idx"], f.get("name")))
            problems += 1
    if problems:
        print("FAIL: %d data problems" % problems)
        return 1

    headers = collect_headers()
    work = tempfile.mkdtemp(prefix="cppref_")
    try:
        rc, err = compile_src(cxx, build_source(entries, headers), work, "all")
        if rc == 0:
            print("OK: all %d examples compile together (%s, C++17)" % (len(entries), cxx))
            return 0
        print("Combined compile failed; checking each example separately...")
        failed = 0
        for f in entries:
            rc, err = compile_src(cxx, build_source([f], headers), work, "ex_%d" % f["_idx"])
            if rc != 0:
                failed += 1
                print("FAIL [%s] %s: %s" % (f["scope"], f["name"], first_error(err)))
        if failed == 0:
            print("FAIL: combined build failed but each example alone passes (name clash?):")
            print(first_error(err))
            return 1
        print("FAIL: %d of %d examples do not compile" % (failed, len(entries)))
        return 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
