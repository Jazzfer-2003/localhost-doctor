# Localhost Doctor

> **"Stop reinstalling XAMPP. Let the AI diagnose your localhost."**

An [MCP](https://modelcontextprotocol.io) server that diagnoses broken local dev
stacks (XAMPP / WAMP on Windows). Plug it into any MCP client (ZCode, Claude
Desktop, Cursor, ...) and ask *"why won't my localhost start?"* — the agent gets
real answers from your machine: running processes, listening ports, and log
files. No more blind reinstalls that wipe your databases.

## Why

Localhost breaks in three predictable ways:

1. **Port already taken** — IIS, Skype, VMware or a leftover process owns port 80/3306.
2. **Crashes on startup** — bad config, damaged InnoDB files, missing VC++ runtime. The cause is always in a log file beginners never find.
3. **The shutdown thing** — you clicked Stop, but `httpd.exe`/`mysqld.exe` is still lurking in the background, so the *next* start mysteriously fails.

Localhost Doctor answers all three, because the truth always lives in the same
three places: **running processes, listening ports, and log files.**

## Tools

| Tool | What it does |
|------|--------------|
| `diagnose_stack()` | One-shot health check: stack processes, port owners (80/8080/443/3306), HTTP probe, Windows services — with a verdict (`healthy` / `degraded` / `port conflict`) and concrete issues. |
| `check_port(port)` | Who is listening on a port, by name and PID, and whether that's expected. |
| `read_error_logs(component)` | Tails Apache/MySQL error logs, filters the error lines, and explains them via the knowledge base. |
| `explain_symptom(text)` | Paste any error ("MySQL shutdown unexpectedly") → ranked causes and fixes from the knowledge base. |

All diagnostics are **read-only**. Mutating fixes (switch port, kill process)
are planned for v2 behind explicit user approval.

## Setup

```bash
pip install -e .
```

Register it with your MCP client:

```json
{
  "mcpServers": {
    "localhost-doctor": {
      "command": "python",
      "args": ["-m", "localhost_doctor.server"]
    }
  }
}
```

If your XAMPP/WAMP lives outside the standard folders (`C:\xampp`, `C:\wamp64`, ...),
set `XAMPP_HOME` to the install root.

## The 3-minute demo

1. Start something that squats port 80 → Apache fails → ask *"why won't my localhost start?"* → the doctor names the process and suggests the port switch.
2. Kill MySQL mid-write → ask again → the doctor reads the MySQL error log and explains the corruption.
3. Everything stopped → *"localhost refused to connect"* → the doctor says nothing is listening and points at the start button.

## Contributing symptoms

The knowledge base is [src/localhost_doctor/kb/symptoms.yaml](src/localhost_doctor/kb/symptoms.yaml)
— a list of `match` patterns → `title`, `causes`, `fixes`. PRs adding new
failure modes (Laragon, Docker Desktop, nginx, Postgres, ...) are very welcome.

## Roadmap

- [ ] v2: guarded fixes (`switch_apache_port`, `free_port`, `restart_service`) with backup-first edits
- [ ] WAMP/Laragon layout coverage
- [ ] Publish to PyPI for `uvx localhost-doctor` usage
- [ ] Community symptom packs

## License

MIT
