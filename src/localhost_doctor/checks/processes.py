"""Detect stack processes (httpd, mysqld, ...) including zombie leftovers."""

import csv
import io
import subprocess
from dataclasses import dataclass

STACK_PROCESSES = {
    "httpd.exe",
    "mysqld.exe",
    "apache.exe",
    "php.exe",
    "php-cgi.exe",
    "wampmanager.exe",
}


@dataclass
class Proc:
    name: str
    pid: int


def running_processes() -> list[Proc]:
    out = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=30
    ).stdout
    procs = []
    for row in csv.reader(io.StringIO(out)):
        if len(row) >= 2:
            try:
                procs.append(Proc(name=row[0], pid=int(row[1])))
            except ValueError:
                continue
    return procs


def find_stack_processes() -> dict[str, list[int]]:
    """Map stack process name -> list of running PIDs."""
    found: dict[str, list[int]] = {}
    for proc in running_processes():
        name = proc.name.lower()
        if name in STACK_PROCESSES:
            found.setdefault(name, []).append(proc.pid)
    return found
