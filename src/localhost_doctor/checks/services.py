"""Check for Apache/MySQL installed as Windows services (XAMPP/WAMP optional mode)."""

import subprocess

SERVICE_NAMES = ["Apache2.4", "apache", "mysql", "MySQL", "MySQL80", "wampapache64", "wampmysqld64"]


def service_status() -> dict[str, str]:
    """Return {service_name: state} for stack-related Windows services found
    on this machine. Absent names are skipped (XAMPP often runs as console
    apps instead of services)."""
    statuses = {}
    for name in SERVICE_NAMES:
        try:
            result = subprocess.run(
                ["sc", "query", name], capture_output=True, text=True, timeout=10
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            continue
        state = "UNKNOWN"
        for line in result.stdout.splitlines():
            if "STATE" in line and ":" in line:
                state = line.split(":", 1)[1].strip()
                break
        statuses[name] = state
    return statuses
