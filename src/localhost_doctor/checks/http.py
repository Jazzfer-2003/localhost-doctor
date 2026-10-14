"""Probe whether localhost actually answers HTTP."""

import urllib.error
import urllib.request


def probe(url: str = "http://localhost/", timeout: float = 2.0) -> dict:
    """GET `url`; any HTTP response counts as reachable, even a 4xx/5xx."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return {"url": url, "reachable": True, "status": response.status}
    except urllib.error.HTTPError as exc:
        return {"url": url, "reachable": True, "status": exc.code}
    except Exception as exc:  # connection refused, timeout, DNS, ...
        return {"url": url, "reachable": False, "error": str(exc)}
