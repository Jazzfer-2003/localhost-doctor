"""Locate a local XAMPP/WAMP installation and map its file layout."""

import os
from pathlib import Path

CANDIDATE_ROOTS = [
    r"C:\xampp",
    r"D:\xampp",
    r"E:\xampp",
    r"C:\wamp64",
    r"D:\wamp64",
    r"C:\wamp",
]


def _layout(root: Path) -> dict:
    """Return the stack layout for a detected install root."""
    if "wamp" in root.name.lower():
        return {
            "found": True,
            "stack": "WAMP",
            "root": str(root),
            "apache_error_log": str(root / "logs" / "apache_error.log"),
            "mysql_error_log": str(root / "logs" / "mysql.log"),
            "httpd_conf": None,
            "my_ini": None,
        }
    return {
        "found": True,
        "stack": "XAMPP",
        "root": str(root),
        "apache_error_log": str(root / "apache" / "logs" / "error.log"),
        "mysql_error_log": str(root / "mysql" / "data" / "mysql_error.log"),
        "httpd_conf": str(root / "apache" / "conf" / "httpd.conf"),
        "my_ini": str(root / "mysql" / "bin" / "my.ini"),
    }


def find_install() -> dict:
    """Detect the local XAMPP/WAMP install. Override with the XAMPP_HOME or
    LOCALHOST_DOCTOR_HOME environment variable for custom locations."""
    env_home = os.environ.get("LOCALHOST_DOCTOR_HOME") or os.environ.get("XAMPP_HOME")
    roots = ([Path(env_home)] if env_home else []) + [Path(p) for p in CANDIDATE_ROOTS]
    for root in roots:
        if not root or not root.is_dir():
            continue
        if (root / "apache").is_dir() and (root / "mysql").is_dir():
            return _layout(root)
        if root.name.lower().startswith("wamp") and (root / "bin").is_dir():
            return _layout(root)
    return {
        "found": False,
        "hint": "No XAMPP/WAMP install found. Set the XAMPP_HOME environment variable to your install folder.",
    }
