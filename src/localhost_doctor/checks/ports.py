"""TCP port inspection via netstat/tasklist. Windows-first, stdlib only."""

import csv
import io
import subprocess
from dataclasses import dataclass

# States that must never be mistaken for an active listener.
_NON_LISTEN = {"ESTABLISHED", "TIME_WAIT", "CLOSE_WAIT", "SYN_SENT", "BOUND", "BINDING"}


@dataclass
class PortListener:
    port: int
    pid: int | None
    address: str


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    return result.stdout


def listening_ports() -> list[PortListener]:
    """Parse `netstat -ano -p tcp` and return sockets that look like listeners.

    State words are localized on non-English Windows, so a row is treated as a
    listener when its remote endpoint is the wildcard 0.0.0.0:0 / [::]:0 and
    the state is not one of the known non-listening states.
    """
    listeners = []
    for line in _run(["netstat", "-ano", "-p", "tcp"]).splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "TCP":
            continue
        local, remote = parts[1], parts[2]
        if not remote.endswith(":0"):
            continue
        state = parts[3].upper() if len(parts) >= 5 else ""
        if state in _NON_LISTEN:
            continue
        try:
            pid = int(parts[-1])
        except ValueError:
            pid = None
        port_str = local.rsplit(":", 1)[-1]
        try:
            port = int(port_str)
        except ValueError:
            continue
        listeners.append(PortListener(port=port, pid=pid, address=local))
    return listeners


def pid_name(pid: int | None) -> str | None:
    """Resolve a PID to a process name via tasklist CSV output (locale-proof)."""
    if pid is None or pid <= 0:
        return None
    out = _run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"]).strip()
    if not out or not out.startswith('"'):
        return None
    try:
        return next(csv.reader(io.StringIO(out)))[0]
    except (StopIteration, IndexError):
        return None


def port_owner(port: int) -> dict | None:
    """Return the process listening on `port`, or None if the port is free."""
    for listener in listening_ports():
        if listener.port == port:
            return {
                "port": port,
                "pid": listener.pid,
                "process": pid_name(listener.pid),
                "address": listener.address,
            }
    return None
