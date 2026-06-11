# 🎄 Hackyholidays CTF

> **Platform:** Hacker101 CTF | **Difficulty:** `moderate` | **Flags:** `12/12`

---

## Attack Chain Summary

```
robots.txt -> hidden directory -> Flag 1
F12 source -> new site location -> Flag 2
People Rater: Base64 ID IDOR (id=4 -> id=1) -> Flag 3
Secure Login: brute-force user/pass -> Base64 cookie -> admin=true -> zip crack -> Flag 4
Swag Shop: gobuster /api/sessions -> Base64 session takeover -> /api/user?uuid= -> Flag 5
Forum: GitHub leaked DB creds -> phpMyAdmin -> crack admin MD5 -> login as grinch -> Flag 6
Hate Mail Generator: SSTI via preview_markup/preview_data -> admin template -> Flag 7
... (Flags 8-11: staff intranet, additional SSRF/IDOR challenges)
Final: DDoS simulator -> Base64 payload -> swap IP to localhost -> crack hash (rockyou) -> SSRF Grinch's own server -> Flag 12
```

---

## Application Overview

A 12-flag holiday-themed CTF released as a series of connected challenges. Each flag unlocks access to the next stage. The chain mixes recon (robots.txt, source inspection), IDOR via Base64-encoded IDs, broken authentication, cookie tampering, password cracking, leaked credentials on GitHub, Server-Side Template Injection (SSTI), and a final SSRF that turns the attacker's tooling against the Grinch's own server.

---

## Flag 1 — robots.txt Recon

The landing page just says "keep out" with no visible links. Check:

```
/robots.txt
```

Reveals the flag and a hidden directory path to the next stage.

---

## Flag 2 — Hidden Site Relocation

Visiting the directory from `robots.txt` shows the Grinch "moved" the site. Press **F12** and inspect the page source/network requests — the new site URL is hardcoded in there along with the flag.

---

## Flag 3 — People Rater (Base64 IDOR)

The new site has 8 sub-challenges. **People Rater** lists names; clicking one sends a request like:

```
/people-rater/entry?id=eyJpZCI6NH0=
```

Decode the `id` parameter (Base64 -> JSON):

```json
{"id":4}
```

The visible list goes from id=2 upward — id=1 is missing. Request it directly:

```
/people-rater/entry?id=eyJpZCI6MX0K
```
(`{"id":1}` Base64-encoded)

Flag appears in the response — classic IDOR via a predictable encoded identifier.

---

## Flag 4 — Secure Login (Brute Force + Cookie Tamper + Zip Crack)

**Step 1 — Username brute-force:**

The login form returns `"Invalid username"` for wrong usernames. Use Burp Intruder with a username wordlist. Found username:

```
access
```

**Step 2 — Password brute-force:**

Same technique, now targeting the password field with username=`access`. Found password:

```
computer
```

**Step 3 — Login** -> page shows "No Files To Download". Inspect cookies — one is Base64-encoded:

```
{"user":"access","admin":false}
```

**Step 4 — Tamper the cookie**, set `"admin":true`, re-encode to Base64, replace the cookie. Reloading the page now shows a downloadable file: `my_secure_files_not_for_you.zip` — password protected.

**Step 5 — Crack the zip with rockyou:**

```bash
fcrackzip -D -p rockyou.txt -u my_secure_files_not_for_you.zip
```

Inside the zip is the flag.

---

## Flag 5 — Grinch Swag Shop (Session Takeover via gobuster)

**Step 1 — Fuzz for hidden API paths:**

```bash
gobuster dir -u https://TARGET/ -w common.txt
```

Found:
```
/api/sessions
```

**Step 2 — Decode session list:**

`/api/sessions` returns a list of Base64-encoded session tokens. Decode each one — one is noticeably longer than the rest, suggesting more data (likely an admin/privileged session).

**Step 3 — Use that session to query the user API:**

```
/api/user/?uuid=C7DCCE-0E0DAB-B20226-FC92EA-1B9043
```

(replace with the UUID decoded from the longer session)

Flag appears in the user data response.

---

## Flag 6 — Forum (Leaked GitHub Credentials + MD5 Crack)

**Step 1 — Reconnaissance:**

A read-only forum, with a `/phpmyadmin` login that doesn't yield to brute-force or SQLi.

**Step 2 — Search GitHub** for the project/company name — find a commit history containing leaked database credentials:

```
login: forum
password: 6HgeAZ0qC9T6CQIqJpD
```

**Step 3 — Login to phpMyAdmin**, browse the `users` table. Find `grinch`'s account with an MD5-hashed password.

**Step 4 — Crack the hash** via crackstation.net:

```
login: grinch
password: BahHumbug
```

**Step 5 — Login to the forum as grinch** -> Flag appears.

---

## Flag 7 — Hate Mail Generator (SSTI)

The app generates email previews from templates. The default template is `cbdj3_grinch_header.html`; an admin-only template `38dhs_admins_only_header.html` exists but isn't directly accessible.

**Payload (Server-Side Template Injection):**

```
preview_markup=hello{{template:cbdj3_/*grinch*/_header.html}}{{77}}&preview_data={"name":"admin","email":"admin@admin.com","admin":true,"administrator":true,"77":"{{template:38dhs_/*admins_only*/_header.html}}"}
```

This abuses the template engine to nest a reference to the restricted admin template inside a field of the data object, bypassing the direct access restriction. The rendered output includes the admin template's content — and the flag.

---

## Flags 8–11 — Intranet Stage

The next stage is hosted on a staff intranet subdomain. It includes additional challenges around:

- `/staff_info/` employee directory with background API calls (further IDOR)
- PIN-based access protected by rate limiting, bypassed using `X-Forwarded-For` header rotation with Burp Intruder (Battering Ram, range 0000-9999)
- LFI via a `template=` parameter on a diary/notes page
- Further session/IDOR chaining similar to Flags 3 and 5

Each of these follows the same pattern as earlier flags: fuzz for hidden endpoints, decode any encoded identifiers, and test IDOR/LFI on parameters that reference files or records.

---

## Flag 12 — DDoS Simulator (SSRF Against the Grinch)

**Step 1 — Goal:** the final page lets you "launch a DDoS" against a target IP. The objective is to redirect this attack at the Grinch's own infrastructure (`127.0.0.1` / `localhost`).

**Step 2 — Capture the request in Burp.** The payload field is Base64-encoded. Decode it (CyberChef) — it contains a target IP plus a hash.

**Step 3 — Crack the hash** with John the Ripper + rockyou:

```bash
john --wordlist=rockyou.txt hash.txt
```

Cracked value: `mrgrinch463` + target (the hash is derived from a fixed secret combined with the target string).

**Step 4 — Forge the payload:**

Replace the IP with `localhost`/`127.0.0.1`, recompute the hash using `mrgrinch463` + `localhost`, Base64-encode the new payload, and send it.

The "DDoS" now targets the Grinch's own server — completing the chain and awarding the final flag.

---

## Why It Works

| Vulnerability | Root Cause |
|---|---|
| Information Disclosure | `robots.txt` and page source leak hidden paths and site relocations |
| IDOR via Base64 IDs | Sequential record IDs encoded in Base64, no ownership check |
| Username Enumeration | Distinct "Invalid username" vs "Invalid password" messages enable brute-force |
| Insecure Cookie Design | Privilege flags (`admin`) stored client-side in a Base64 JSON cookie |
| Weak Zip Encryption | Password-protected zip crackable with a common wordlist |
| Session Token Predictability | All sessions use the same encoding scheme — any session can be decoded and reused |
| Credential Leakage via VCS | Database credentials committed to GitHub history |
| Weak Password Hashing | MD5 passwords reversible via rainbow tables |
| SSTI | User-controlled template names allow referencing restricted templates |
| Rate Limit Bypass | `X-Forwarded-For` spoofing resets per-IP rate limits |
| SSRF | DDoS target IP and hash are client-controlled and not validated server-side |

---

## Key Payloads / Commands

```bash
# Flag 4 - crack zip
fcrackzip -D -p rockyou.txt -u my_secure_files_not_for_you.zip

# Flag 5 - directory fuzz
gobuster dir -u https://TARGET/ -w common.txt

# Flag 7 - SSTI
preview_markup=hello{{template:cbdj3_/*grinch*/_header.html}}{{77}}&preview_data={"name":"admin","email":"admin@admin.com","admin":true,"administrator":true,"77":"{{template:38dhs_/*admins_only*/_header.html}}"}

# Flag 12 - crack DDoS auth hash
john --wordlist=rockyou.txt hash.txt
```
