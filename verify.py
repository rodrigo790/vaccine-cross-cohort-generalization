"""Verify the released result bytes, including every table and figure."""

from pathlib import Path
import hashlib
import json

if __name__ == "__main__":
    expected = json.loads(Path("results.sha256.json").read_text(encoding="utf-8-sig"))
    actual = {
        p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in Path("results").iterdir()
        if p.is_file()
    }
    if actual != expected:
        raise SystemExit("Released result inventory or checksum mismatch")
    print(f"Verified {len(actual)} result files")
