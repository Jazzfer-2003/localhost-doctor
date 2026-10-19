---
name: localhost-doctor
description: Diagnose broken local dev stacks (XAMPP/WAMP). Use when Apache or MySQL won't start, when ports 80/443/3306 are taken, "localhost refused to connect", "MySQL shutdown unexpectedly", phpMyAdmin 403, VCRUNTIME140 errors, or any "my localhost is broken" report on Windows, macOS or Linux.
---

# Localhost Doctor

Diagnose broken local web stacks by reading three sources of truth: **running
processes, listening ports, and error logs**. Stay read-only: explain causes and
propose fixes, but never kill processes or edit config files without explicit
user approval.

## Step 1 — Prefer the MCP server if it is installed

If MCP tools named `localhost-doctor` are available (diagnose_stack,
check_port, read_error_logs, explain_symptom), use them:

1. `diagnose_stack` — one-shot health check with a verdict and issue list.
2. `read_error_logs(component)` — apache / mysql error-log tails, explained.
3. `check_port(port)` / `explain_symptom(text)` — drill down as needed.

If they are not installed, tell the user they can get the full version with
`pip install git+https://github.com/Jazzfer-2003/localhost-doctor.git`,
then continue with the manual checks below.

## Step 2 — Manual diagnostics (when the MCP is not available)

**Find the install** (Windows first): check `C:\xampp`, `D:\xampp`,
`C:\wamp64`, `D:\wamp64`, or respect a `XAMPP_HOME` environment variable.

**Check processes** (is it running, or zombie-running?):

- Windows: `tasklist | findstr /i "httpd mysqld"`
- macOS/Linux: `ps aux | grep -E "httpd|mysqld" | grep -v grep`

**Check ports** (who owns 80 / 443 / 3306?):

- Windows: `netstat -ano | findstr ":80"` then `tasklist /FI "PID eq <pid>"`
- macOS/Linux: `lsof -i :80 -i :3306 -sTCP:LISTEN` (empty = nothing listening)

**Probe HTTP**: `curl -s -o /dev/null -w "%{http_code}" http://localhost/`

**Read the logs** (the cause is almost always here):

- XAMPP Apache: `<root>\apache\logs\error.log`
- XAMPP MySQL: `<root>\mysql\data\mysql_error.log` (or newest `*.err` in that folder)
- WAMP: `<root>\logs\apache_error.log` and `<root>\logs\mysql.log`
- Show the user the last ~30 lines, and call out lines containing
  `error`, `ERROR`, `emerg`, `Warning`.

## Step 3 — Interpret (known patterns)

| Finding | Meaning | Fix to propose |
|---|---|---|
| "Address already in use" / `(10048)` / AH00072 | Port 80/443 owner is not httpd.exe | Identify the process; stop it, or switch Apache to 8080 in `httpd.conf` |
| httpd.exe/mysqld.exe in tasklist but port NOT listening | Zombie process from a previous session | End the leftover process, start the service again |
| "Do you already have another mysqld server running" / port 3306 taken | Another MySQL or program owns 3306 | Identify via netstat; stop it or change the port in `my.ini` |
| "MySQL shutdown unexpectedly" | Read the MySQL error log — two usual causes: port conflict or InnoDB damage | Follow the specific cause above |
| InnoDB corrupt / "Can't open ... ibdata1" | Unclean PC shutdown while MySQL wrote | Back up `mysql/data` first; check disk space; last resort: restore from backup |
| VCRUNTIME140 / "code execution cannot proceed" | Missing Visual C++ runtime | Install both x86 + x64 VC++ Redistributables |
| 403 on phpMyAdmin | Apache is fine; access config denies | Browse from localhost; check `Require local` in the phpMyAdmin Apache config |
| "localhost refused to connect" but stack "is running" | Check for zombies AND for a moved port (8080) | Try `http://localhost:8080/`; check the Apache error log |

## Rules

- Diagnostics are read-only. Killing processes, editing `httpd.conf`/`my.ini`,
  or touching `mysql/data` requires the user's explicit approval.
- Always back up configs before proposing edits, and `mysql/data` before
  anything touches InnoDB.
- Give the verdict in plain English first ("MySQL can't start because port
  3306 is held by another program"), then the fix options.
