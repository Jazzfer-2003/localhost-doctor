"""Smoke test: run the real (read-only) diagnostics against this machine.

Usage: python tests/test_smoke.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from localhost_doctor import knowledge, logs, xampp  # noqa: E402
from localhost_doctor.checks import http, ports, processes  # noqa: E402


def check(name: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {name}" + (f" - {detail}" if detail else ""))
    if not condition:
        globals()["FAILED"] = True


def main() -> None:
    globals()["FAILED"] = False

    # 1. netstat parsing works
    listeners = ports.listening_ports()
    check("listening_ports parses", isinstance(listeners, list), f"{len(listeners)} listeners")

    # 2. port owner resolution works (any port from the list)
    some = next(iter(listeners), None)
    if some and some.pid:
        name = ports.pid_name(some.pid)
        check("pid_name resolves", name is not None, f"PID {some.pid} -> {name}")
    else:
        check("pid_name resolves", True, "no listeners to test (ok)")

    # 3. tasklist full scan works
    procs = processes.running_processes()
    check("running_processes parses", len(procs) > 0, f"{len(procs)} processes")
    stack_procs = processes.find_stack_processes()
    print(f"    stack processes on this machine: {stack_procs}")

    # 4. install detection
    install = xampp.find_install()
    check("install detection", "found" in install, json.dumps(install)[:120])

    # 5. log tailing handles missing and real files
    missing = logs.tail(r"C:\definitely\not\here\error.log")
    check("log tail on missing file", missing["exists"] is False)
    if install.get("found"):
        for key in ("apache_error_log", "mysql_error_log"):
            report = logs.tail(install[key])
            print(f"    {key}: exists={report['exists']} issues={len(report['issues'])}")

    # 6. knowledge base matches a classic Apache port error
    results = knowledge.explain(
        "(10048) Only one usage of each socket address : AH00072: make_sock: "
        "could not bind to address 0.0.0.0:80"
    )
    check("knowledge match: apache port in use", any(r["id"] == "apache_port_in_use" for r in results))
    results = knowledge.explain("MySQL shutdown unexpectedly")
    check("knowledge match: mysql shutdown", any(r["id"] == "mysql_shutdown_unexpectedly" for r in results))
    check("knowledge no false match", knowledge.explain("the weather is nice today") == [])

    # 7. MCP server exposes exactly the four tools
    from localhost_doctor.server import mcp

    tools = asyncio.run(mcp.list_tools())
    names = sorted(t.name for t in tools)
    check(
        "mcp tools registered",
        names == ["check_port", "diagnose_stack", "explain_symptom", "read_error_logs"],
        str(names),
    )

    if globals()["FAILED"]:
        sys.exit(1)
    print("\nAll smoke checks passed.")


if __name__ == "__main__":
    main()
