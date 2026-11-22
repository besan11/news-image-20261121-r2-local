#!/usr/bin/env python3
"""Self-check for the news-image-20261121 r2 entry.

Four checks, in order:

1. Entry gates: entry.png exists, is a PNG, is at most 1024x1024,
   and is under the 1 MiB cap.
2. Static scan: main.py must never delete the output directory or
   reach the network -- it may only read entry.png and write the one
   destination file.
3. Two runs: main.py runs twice into two fresh directories; both
   outputs must be byte-identical to each other and to entry.png.
4. Grader rehearsal: the repo is copied read-only, the output
   directory is pre-created and holds a stale file, and main.py runs
   against that copy. It must exit 0, write identical bytes, and
   leave the stale file alone.

Exit 0 only when every check passes.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")
MAIN = os.path.join(HERE, "main.py")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def fail(msg):
    print("FAIL: %s" % msg, file=sys.stderr)
    return 1


def main():
    # 1. Entry gates.
    if not os.path.isfile(ENTRY):
        return fail("entry.png is missing")
    size = os.path.getsize(ENTRY)
    if size > 1048576:
        return fail("entry.png is %d bytes, over 1 MiB" % size)
    from PIL import Image
    with Image.open(ENTRY) as im:
        if im.format != "PNG":
            return fail("entry.png is not PNG")
        if im.size[0] > 1024 or im.size[1] > 1024:
            return fail("entry.png is %s, over 1024x1024" % (im.size,))
        dims = im.size
    print("gate: entry.png PNG %s, %d bytes" % (dims, size))

    # 2. Static scan of main.py.
    with open(MAIN, "r", encoding="utf-8") as f:
        src = f.read()
    for banned in ("shutil.rmtree", "os.rmdir", "os.remove", "unlink(",
                   "os.system", "subprocess", "urllib", "socket",
                   "requests", "http"):
        if banned in src:
            return fail("main.py contains %r" % banned)
    print("static: main.py never deletes the output dir, never uses "
          "the network")

    # 3. Two runs, identical bytes.
    digests = []
    for i in range(2):
        out = tempfile.mkdtemp(prefix="makefun-r2-run%d-" % i)
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=out)
        r = subprocess.run([sys.executable, MAIN], env=env,
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return fail("main.py run %d exited %d: %s"
                        % (i + 1, r.returncode, r.stderr.strip()))
        got = os.path.join(out, "entry.png")
        if not os.path.isfile(got):
            return fail("run %d wrote no entry.png" % (i + 1))
        digests.append(sha(got))
        shutil.rmtree(out)
        print("run %d: exit 0, sha256 %s" % (i + 1, digests[-1]))
    if digests[0] != digests[1]:
        return fail("two runs produced different bytes")
    if digests[0] != sha(ENTRY):
        return fail("run output differs from entry.png")
    print("identity: both runs match entry.png byte for byte")

    # 4. Grader rehearsal: read-only repo copy, pre-created output dir.
    with tempfile.TemporaryDirectory(prefix="makefun-r2-grader-") as tmp:
        repo = os.path.join(tmp, "repo")
        shutil.copytree(HERE, repo, ignore=shutil.ignore_patterns(
            "__pycache__", ".git", "*.pyc"))
        for root, _dirs, files in os.walk(repo):
            for name in files:
                os.chmod(os.path.join(root, name), 0o444)
        out = os.path.join(tmp, "output")
        os.makedirs(out)
        stale = os.path.join(out, "stale.txt")
        with open(stale, "w", encoding="utf-8") as f:
            f.write("must survive")
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=out)
        r = subprocess.run([sys.executable, os.path.join(repo, "main.py")],
                           env=env, capture_output=True, text=True,
                           timeout=10)
        if r.returncode != 0:
            return fail("grader rehearsal exited %d: %s"
                        % (r.returncode, r.stderr.strip()))
        if not os.path.isfile(stale):
            return fail("grader rehearsal deleted a file in the output dir")
        if sha(os.path.join(out, "entry.png")) != sha(ENTRY):
            return fail("grader rehearsal output differs from entry.png")
        print("grader rehearsal: read-only repo, pre-created output dir, "
              "stale file kept, exit 0, identical bytes")
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
