# Hacker101 CTF Writeups

Personal writeups for Hacker101 CTF challenges — SQL injection, IDOR, XSS, SSRF, file upload, cryptography, mobile, and more. Each folder contains a clean step-by-step `README.md` with payloads and the reasoning behind each exploit.

---

## Progress

| Challenge | Difficulty | Flags | Status |
|---|---|---|---|
| [Photo Gallery](./photo-gallery/README.md) | Moderate | 3/3 | ✅ |
| [Postbook](./postbook/README.md) | Easy | 7/7 | ✅ |
| [Cody's First Blog](./codys-first-blog/README.md) | Moderate | 3/3 | ✅ |
| [Petshop Pro](./petshop-pro/README.md) | Easy | 3/3 | ✅ |
| [Ticketastic: Live Instance](./Ticketastic%3A%20Live%20Instance/README.md) | Moderate | 2/2 | ✅ |
| [Tempimage](./tempimage/README.md) | Moderate | 2/2 | ✅ |
| [Model E1337](./model-e1337/README.md) | Hard | 2/2 | ✅ |
| [Intentional Exercise](./Intentional%20exercise/README.md) | Moderate | 1/1 | ✅ |
| [BugDB v1](./BugDB%20v1/README.md) | Easy | 1/1 | ✅ |
| [BugDB v2](./BugDB%20v2/README.md) | Moderate | 2/2 | ✅ |
| [XSS Playground — zseano](./XSS%20Playground%20%E2%80%94%20zseano/README.md) | Easy | 1/1 | ✅ |
| [OSU CTF](./OSU%20CTF/README.md) | Moderate | 1/1 | ✅ |
| [H1 Thermostat](./H1%20thermostat/README.md) | Easy | 2/2 | ✅ |
| [RTFM](./RTFM/README.md) | Moderate | 8/8 | ✅ |
| [Grayhatcon CTF](./Grayhatcon%20CTF/README.md) | Moderate | 4/4 | ✅ |
| [Hackyholidays CTF](./Hackyholidays%20ctf/README.md) | Moderate | 12/12 | ✅ |
| [Y2FuIHlvdSByZWNvbj8/](./Y2FuIHlvdSByZWNvbj8/README.md) | Moderate | 3/3 | ✅ |


---

## Vulnerability Index

A quick reference to which writeups cover which vulnerability classes:

| Category | Labs |
|---|---|
| **SQL Injection** | Photo Gallery, Ticketastic, Grayhatcon CTF |
| **IDOR / Broken Access Control** | Postbook, Petshop Pro, Grayhatcon CTF, Hackyholidays CTF |
| **XSS / Stored Injection** | Cody's First Blog, Petshop Pro, XSS Playground |
| **File Upload / RCE** | Tempimage, Y2FuIHlvdSByZWNvbj8/ |
| **CSRF** | Ticketastic: Live Instance |
| **XXE** | Model E1337 |
| **PRNG / Cryptanalysis** | Model E1337 |
| **GraphQL** | BugDB v1, BugDB v2 |
| **SSRF** | RTFM, Grayhatcon CTF |
| **Mobile / APK Reverse Engineering** | H1 Thermostat, Intentional Exercise |
| **Auth Bypass / Cookie Tampering** | Postbook, Grayhatcon CTF, Hackyholidays CTF |

---

## Tools Used

`Burp Suite` · `Ghauri` · `ffuf` · `feroxbuster` · `feroxbuster` · `jadx` · `fcrackzip` · `Python`

---

## Notes

- Flags are redacted in writeups — only payloads and methodology are shown.
- Each writeup follows the same format: attack chain summary, step-by-step exploitation, root cause table, and reusable payloads.
- All labs solved on Hacker101 CTF (https://ctf.hacker101.com).


> *If these writeups helped you learn something new, consider giving this repo a ⭐ to help others find it!*
