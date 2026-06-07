# 🐾 Petshop Pro

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy` &nbsp;|&nbsp; **Flags:** `3/3` ✅

---

## ⛓️ Attack Chain

```
Hidden field price manipulation → Admin bypass via IDOR → Stored XSS in product name → Flag on cart page
```

---

## 🔍 Application Overview

A pet shop where you can add items to cart and checkout. The app has three vulnerabilities: a hidden price field on checkout, an unprotected edit page accessible by ID, and stored XSS in product fields that triggers on the cart page.

---

## 🚩 Flag 0 — Hidden Field Price Manipulation

Add an item to the cart and go to checkout. Intercept the request in Burp Suite — there is a hidden `price` field in the form.

Either inspect the page source and remove `type="hidden"` to expose the field, or modify it directly in Burp:

```
price=100  →  price=1
```

Submit the checkout. Flag appears in the response.

---

## 🚩 Flag 1 — Admin Bypass via IDOR

No need to brute force the login. The edit page is directly accessible without authentication:

```
/edit?id=0   ← cat
/edit?id=1   ← puppy
```

Navigate to either URL. Flag appears on the edit page — no credentials required.

---

## 🚩 Flag 2 — Stored XSS in Product Name

From the edit page (`/edit?id=0`), inject an XSS payload into the **name** field:

```html
<image src/onerror=prompt(8)>
```

Save the changes. Add the item to the cart and navigate to `/cart`. The payload executes and the flag appears in the name field on the cart page.

> 💡 The hint says *"bugs don't always appear where data is entered"* — meaning the XSS triggers on `/cart`, not on the edit page itself.

---

## 🧠 Why It Works

| Vulnerability | Root Cause |
|---|---|
| Price manipulation | Checkout relies on a client-side hidden field — server never validates price server-side |
| Admin bypass (IDOR) | Edit page uses sequential IDs with no authentication check |
| Stored XSS | Product name stored raw in DB and rendered unsanitized on the cart page |

---

## 📋 Payloads

```
# Flag 0 — Modify hidden price field
price=1

# Flag 1 — Direct access to edit page
/edit?id=0
/edit?id=1

# Flag 2 — XSS payload in name field
<image src/onerror=prompt(8)>
```
