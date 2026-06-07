# 📱 Intentional Exercise

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Moderate` &nbsp;|&nbsp; **Flags:** `1/1` ✅

---

## ⛓️ Attack Chain

```
Decompile APK → Find secret key + path in source code → Generate SHA-256 hash → Access flag URL
```

---

## 🔍 Application Overview

An Android app that loads a WebView pointing to `/appRoot`. The app generates a SHA-256 hash from a hardcoded secret key and the URL path, then appends it as a `&hash=` parameter. The server validates this hash before serving content — but the secret key is hardcoded in the APK source code, making it trivial to forge any request.

---

## 🚩 Flag — Hash Forgery via Hardcoded Secret Key

**Step 1 — Decompile the APK with jadx:**

```bash
jadx-gui intentional-exercise.apk
```

Navigate to `com/hacker101/level13/MainActivity.java`.

**Step 2 — Find the secret key and hash logic:**

```java
MessageDigest messageDigest = MessageDigest.getInstance("SHA-256");
messageDigest.update("s00p3rs3cr3tk3y".getBytes(StandardCharsets.UTF_8));
messageDigest.update(strSubstring.getBytes(StandardCharsets.UTF_8));
webView.loadUrl(str + "&hash=" + String.format("%064x", new BigInteger(1, messageDigest.digest())));
```

The hash is `SHA256("s00p3rs3cr3tk3y" + path)`.

**Step 3 — Visit `/appRoot` to discover the flag path:**

```
https://LABURL/appRoot?&hash=SHA256("s00p3rs3cr3tk3y")
```

The page shows a link to `/flagBearer`.

**Step 4 — Generate the correct hash for `/flagBearer`:**

```python
import hashlib
path = "/flagBearer"
hash = hashlib.sha256(("s00p3rs3cr3tk3y" + path).encode()).hexdigest()
print(f"https://LABURL/appRoot{path}?&hash={hash}")
```

Output hash: `8743a18df6861ced0b7d472b34278dc29abba81b3fa4cf836013426d6256bd5e`

**Step 5 — Access the flag URL:**

```
https://LABURL/appRoot/flagBearer?&hash=8743a18df6861ced0b7d472b34278dc29abba81b3fa4cf836013426d6256bd5e
```

Flag appears in the response.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Hardcoded secret key | `s00p3rs3cr3tk3y` is embedded in the APK source — visible after decompilation |
| Broken authentication | Server trusts the hash as proof of legitimacy, but the key is publicly extractable |
| Insufficient URL validation | No origin check — hash can be generated for any path |

---

## 📋 Payloads

```python
import hashlib

# Generate hash for any path
def get_url(base_url, path):
    h = hashlib.sha256(("s00p3rs3cr3tk3y" + path).encode()).hexdigest()
    return f"{base_url}/appRoot{path}?&hash={h}"

base = "https://LABURL"
print(get_url(base, ""))           # /appRoot page
print(get_url(base, "/flagBearer")) # Flag
```
