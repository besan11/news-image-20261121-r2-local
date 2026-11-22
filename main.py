#!/usr/bin/env python3
"""Copy entry.png into the grader's output directory.

Reads the PNG next to this file and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png. The output directory is treated as
someone else's mount point: this program never removes it and never
empties it -- it only overwrites the single file entry.png. It checks
the PNG signature and the 1 MiB size cap before writing, so a corrupt
or oversized build fails loudly instead of shipping bad bytes.

Standard library only. No network, no writes anywhere except the one
destination file.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
LIMIT = 1048576
MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 2
    with open(SRC, "rb") as f:
        data = f.read()
    if data[:8] != MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    if len(data) > LIMIT:
        print("entry.png is %d bytes, over the 1 MiB cap" % len(data),
              file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, sha256 %s)"
          % (dest, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
