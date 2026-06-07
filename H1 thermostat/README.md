# 🌡️ H1 Thermostat

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy` &nbsp;|&nbsp; **Flags:** `2/2` ✅

---

## ⛓️ Attack Chain

```
Download APK → Decompile with jadx → Read PayloadRequest.java → Both flags hardcoded in source
```

---

## 🔍 Application Overview

An Android thermostat app. The APK contains hardcoded flags inside the decompiled Java source code. No dynamic exploitation needed — pure static analysis.

---

## 🚩 Flag 0 — Hardcoded in POST Request

**Step 1 — Download the APK** from the lab page.

**Step 2 — Decompile with jadx:**

```bash
jadx thermostat.apk
```

Or use the online tool at [jadx.online](https://jadx.online).

**Step 3 — Navigate the source:**

```
AndroidManifest.xml → package: com/hacker101/level11
→ ThermostatActivity.java
→ ThermostatModel.java
→ PayloadRequest.java  ← FLAGS ARE HERE
```

**Flag 0** is hardcoded inside `PayloadRequest.java` — visible in the POST request the app sends to the server when it starts.

---

## 🚩 Flag 1 — Also in PayloadRequest.java

Scroll further down in `PayloadRequest.java`. **Flag 1** is hardcoded in the same file in another code block.

Both flags are in the same file. No emulator, no network interception needed.

> 💡 **Alternative:** Install the APK in an Android emulator, proxy the traffic through Burp Suite, and Flag 0 appears directly in the POST request the app makes on startup.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Hardcoded secrets | Flags embedded directly in Java source — visible after decompilation |
| No obfuscation | Code is not minified or obfuscated — readable as-is after jadx |

---

## 📋 Tools & Commands

```bash
# Decompile APK
jadx thermostat.apk

# Target file
com/hacker101/level11/PayloadRequest.java

# Alternative — search all decompiled files
grep -r "FLAG" ./jadx-output/
```
