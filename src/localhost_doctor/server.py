"""Localhost Doctor MCP server.

Tools (all read-only; mutating fixes are a planned v2):
- diagnose_stack: full health check of the local XAMPP/WAMP stack
- check_port: identify which process holds a TCP port
- read_error_logs: tail Apache/MySQL error logs and explain what's wrong
- explain_symptom: match pasted error text against the knowledge base
"""

import json

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from . import knowledge, logs, xampp
from .checks import http, ports, processes, services

mcp = MCPServer("localhost-doctor")

# All tools are read-only diagnostics; declare it so clients and trust
# scanners know they are safe to call and side-effect free.
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True)

STACK_PROCESS_NAMES = {"httpd.exe", "mysqld.exe", "php-cgi.exe", "apache.exe"}


def _j(data) -> str:
    return json.dumps(data, indent=2, default=str)


def _collect_snapshot() -> dict:
    install = xampp.find_install()
    procs = processes.find_stack_processes()
    owners = {}
    for port in (80, 8080, 443, 3306):
        owner = ports.port_owner(port)
        if owner:
            owners[port] = owner
    # Only probe ports that actually have a listener; refused/timeout on a
    # closed port carries no extra information.
    probes = {}
    for port in (80, 8080):
        if port in owners:
            probes[str(port)] = http.probe(f"http://localhost:{port}/")
        else:
            probes[str(port)] = {"port": port, "reachable": False, "note": "no listener"}
    return {
        "install": install,
        "processes": procs,
        "port_owners": owners,
        "http_probes": probes,
        "windows_services": services.service_status(),
    }


def _analyze(snapshot: dict) -> tuple[str, list[str]]:
    owners = snapshot["port_owners"]
    procs = snapshot["processes"]

    def state(exe: str, ports_of_interest: tuple[int, ...]) -> str:
        running = bool(procs.get(exe))
        listening = any(
            owners.get(p, {}).get("process", "").lower() == exe
            for p in ports_of_interest
            if p in owners
        )
        if listening:
            return "running"
        if running:
            return "hung"  # process alive but port closed: zombie/hung
        return "stopped"

    apache = state("httpd.exe", (80, 8080))
    mysql = state("mysqld.exe", (3306,))
    issues: list[str] = []

    port80 = owners.get(80)
    if apache == "stopped" and port80:
        issues.append(
            f"Port 80 is held by {port80.get('process')} (PID {port80.get('pid')}) - "
            "Apache can't start until that process stops or Apache moves to another port."
        )
    elif apache == "stopped" and 80 not in owners and 8080 not in owners:
        issues.append("Apache is not running (nothing listening on 80/8080).")
    if apache == "hung":
        issues.append(
            "httpd.exe is running but nothing is listening on 80/8080 - likely a zombie "
            "process from a previous session. End httpd.exe and start Apache again."
        )

    port3306 = owners.get(3306)
    if mysql == "stopped" and port3306:
        issues.append(
            f"Port 3306 is held by {port3306.get('process')} (PID {port3306.get('pid')}) - "
            "MySQL can't start until that port is free."
        )
    elif mysql == "stopped" and 3306 not in owners:
        issues.append("MySQL is not running (nothing listening on 3306).")
    if mysql == "hung":
        issues.append(
            "mysqld.exe is running but port 3306 is not listening - likely a leftover/zombie "
            "mysqld. End it and start MySQL again."
        )

    reachable = [p for p, r in snapshot["http_probes"].items() if r.get("reachable")]
    if apache == "running" and not reachable:
        issues.append(
            "Apache owns its port but localhost did not answer HTTP - check the Apache error log."
        )

    if apache == "running" and mysql == "running" and reachable:
        verdict = "healthy"
    elif any("held by" in issue for issue in issues):
        verdict = "port conflict"
    else:
        verdict = "degraded"
    return verdict, issues


@mcp.tool(annotations=READ_ONLY)
def diagnose_stack() -> str:
    """Full health check of the local XAMPP/WAMP stack: which stack processes are
    running, who owns ports 80/8080/443/3306, whether localhost answers HTTP,
    plus a verdict (healthy / degraded / port conflict) and concrete issues."""
    snapshot = _collect_snapshot()
    verdict, issues = _analyze(snapshot)
    result = {
        "verdict": verdict,
        "issues": issues,
        "next_steps": (
            [
                "Call read_error_logs('apache') and read_error_logs('mysql') for the raw causes",
                "Call explain_symptom() with any error text you find",
            ]
            if verdict != "healthy"
            else []
        ),
        "snapshot": snapshot,
    }
    return _j(result)


@mcp.tool(annotations=READ_ONLY)
def check_port(port: int) -> str:
    """Identify which process is listening on a TCP port (e.g. 80, 8080, 3306)
    and what that means for the local stack."""
    owner = ports.port_owner(port)
    if not owner:
        return _j({"port": port, "listening": False, "meaning": "Nothing is listening on this port."})
    name = (owner.get("process") or "").lower()
    if name in STACK_PROCESS_NAMES:
        meaning = "Owned by the local dev stack - this is expected."
    else:
        meaning = (
            f"Held by an outside program ({owner.get('process')}) - this can block "
            "Apache/MySQL from starting."
        )
    return _j({**owner, "listening": True, "meaning": meaning})


@mcp.tool(annotations=READ_ONLY)
def read_error_logs(component: str = "all", tail: int = 30) -> str:
    """Read the tail of Apache/MySQL error logs from the detected install and
    explain error lines via the knowledge base. component: 'apache', 'mysql' or 'all'."""
    install = xampp.find_install()
    if not install.get("found"):
        return _j({"error": "no XAMPP/WAMP install found", "hint": install.get("hint")})
    wanted = {"apache", "mysql"} if component.lower() == "all" else {component.lower()}
    out = {}
    for name, key in (("apache", "apache_error_log"), ("mysql", "mysql_error_log")):
        if name not in wanted:
            continue
        report = logs.tail(install.get(key), tail)
        if report.get("issues"):
            report["explanations"] = knowledge.explain("\n".join(report["issues"]))
        out[name] = report
    return _j(out)


@mcp.tool(annotations=READ_ONLY)
def explain_symptom(text: str) -> str:
    """Explain a localhost symptom or error message. Paste the raw error text,
    e.g. 'localhost refused to connect' or 'MySQL shutdown unexpectedly'."""
    results = knowledge.explain(text)
    if not results:
        return _j(
            {
                "matched": False,
                "hint": "No known pattern matched. Try read_error_logs() to see the raw log tail.",
            }
        )
    return _j({"matched": True, "results": results})


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
