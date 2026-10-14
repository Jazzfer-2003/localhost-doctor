"""Tail stack error logs and pull out the lines that matter."""

import re
from pathlib import Path

# Apache levels + generic error markers found in MySQL logs.
_INTERESTING = re.compile(
    r"\[(?:emerg|alert|crit|error)\]|\[(?:emerg|alert|crit|error):|\bERROR\b|\bError\b:",
    re.IGNORECASE,
)

# Read at most the last 200 KB so a huge log can't blow up memory.
_MAX_BYTES = 200_000


def tail(path: str | None, n: int = 30) -> dict:
    """Return the last `n` lines of `path` plus the error-ish lines.

    If the exact file is missing but sibling *.err files exist (the MySQL
    data-dir naming convention), the newest one is used instead.
    """
    if not path:
        return {"path": None, "exists": False, "lines": [], "issues": []}
    resolved = Path(path)
    if not resolved.is_file() and resolved.parent.is_dir():
        candidates = sorted(resolved.parent.glob("*.err"))
        if candidates:
            resolved = candidates[-1]
    if not resolved.is_file():
        return {"path": str(path), "exists": False, "lines": [], "issues": []}
    raw = resolved.read_bytes()[-_MAX_BYTES:]
    lines = raw.decode(errors="replace").splitlines()[-n:]
    issues = [line for line in lines if _INTERESTING.search(line)]
    return {"path": str(resolved), "exists": True, "lines": lines, "issues": issues[-10:]}
