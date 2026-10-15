# Promotion kit — drafts ready to post

One-time checklist and copy-paste drafts for the first launch push.
Nothing here needs to be perfect — the goal is the first 50 real users.

## One-time setup (do these first)

- [ ] **PyPI**: after the repo's "Publish to PyPI" workflow exists, register a
      pending publisher at https://pypi.org → account settings → publishing
      (owner `Jazzfer-2003`, repo `localhost-doctor`, workflow
      `publish.yml`, environment `pypi`). Then cut a GitHub release `v0.1.0`
      and the package publishes automatically.
- [ ] **Official MCP Registry**: server.json already has the name; submit via
      https://github.com/modelcontextprotocol/registry (open a PR or use their
      submission flow).
- [ ] **Smithery**: https://smithery.ai → submit server (smithery.yaml exists).
- [ ] **Glama**: https://glama.ai/mcp/servers → add server.
- [ ] **PulseMCP**: https://www.pulsemcp.com → submit.
- [ ] Record the **3-minute demo as a GIF** (OBS / ScreenToGif) and drop it
      under the first README heading.

---

## Show HN draft

**Title:**
Show HN: Localhost Doctor – an MCP server that diagnoses broken XAMPP/WAMP stacks

**Body:**

Hi HN! I built Localhost Doctor, an MCP (Model Context Protocol) server that
figures out why a local Apache/MySQL stack is broken.

Every beginner who installs XAMPP eventually hits the same wall: "Apache won't
start", "port 80 in use", or the infamous "MySQL shutdown unexpectedly". The
answer is always in the same three places — running processes, listening ports,
and error logs — but beginners don't know where those are or how to read them.

So I made a small read-only MCP server that your AI assistant (Claude, Cursor,
etc.) can call: it inspects the actual machine, names the process squatting
port 80, tails the MySQL error log, and explains the failure in plain English.
The diagnosis logic is a pattern-matching knowledge base over symptoms
(YAML), so adding a new failure mode is a 10-line contribution.

Install: `pip install localhost-doctor`, then register it with any MCP client.

Repo: https://github.com/Jazzfer-2003/localhost-doctor

Happy to answer questions — especially interested in which stacks to cover
next (Laragon, Docker Desktop, nginx are on the roadmap).

---

## Reddit r/mcp post draft

**Title:**
I made an MCP server that fixes "MySQL shutdown unexpectedly" and other XAMPP errors — it reads ports, processes and logs on your machine

**Body:**

Ever had your AI agent go in circles on "localhost refused to connect"?
The info the agent needs is on the machine: who owns port 80, what's in
`mysql/data/*.err`. I packaged that into a read-only MCP server called
localhost-doctor.

Tools: `diagnose_stack()` (one-shot health check), `check_port(port)`,
`read_error_logs(component)`, `explain_symptom(text)` — all read-only for now,
guarded fixes (kill process / switch port) planned with user approval.

`pip install localhost-doctor` and add it to your MCP client:
```json
{ "mcpServers": { "localhost-doctor": { "command": "python", "args": ["-m", "localhost_doctor.server"] } } }
```

Repo: https://github.com/Jazzfer-2003/localhost-doctor

Which stack should I cover next — Laragon, Docker Desktop, or nginx?

---

## Answer-template for Stack Overflow / r/webdev / r/XAMPP

(Use helpfully — answer the actual question first, mention the tool second.)

> If you want to find the root cause instead of guessing: something is either
> squatting port 80/3306 or the real error is in `apache\logs\error.log` /
> `mysql\data\*.err`. Run `netstat -ano | findstr :80` + `tasklist /FI "PID eq <pid>"`,
> and check those logs. I also built a small open-source tool that automates
> exactly this (localhost-doctor, MIT, on GitHub) if you'd rather have your
> AI assistant do it.

---

## dev.to article outline

1. **Hook**: "MySQL shutdown unexpectedly" — the error every XAMPP user meets,
   50M Stack Overflow views, and the fix is always in a log file beginners
   never open.
2. The three failure modes of localhost (port conflict / startup crash /
   zombie processes).
3. What MCP is in 3 sentences and why "give the AI tools to inspect the
   machine" beats "paste the error into chat".
4. Walkthrough with screenshots: break XAMPP on purpose → ask the agent →
   diagnosis in 30 seconds.
5. Architecture: read-only tools + YAML knowledge base, why symptom patterns
   are a great first PR.
6. Roadmap: guarded fixes, Laragon/Docker/nginx, link to repo.

## Where to post, in order

1. r/mcp (friendly, small, good for first feedback)
2. dev.to article
3. Hacker News Show HN (weekday morning US time; have the PyPI badge live
   before posting)
4. X/Twitter with the GIF, tag @modelcontextprotocol-adjacent folks
5. relevant Discord servers (MCP, Claude, Cursor communities)
