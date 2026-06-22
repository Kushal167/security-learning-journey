# Access Control Vulnerabilities — Study Notes
> PortSwigger Web Security Academy | Access Control Module

---

## What is Access Control?

Access control is about **who can do what** in a system. It sits on top of authentication (who you are) and session management (proving you're still you).

---

## Access Control Models

### DAC — Discretionary Access Control
- The **owner** of a resource decides who can access it
- Example: Sharing a Google Doc and choosing who gets view/edit access

### MAC — Mandatory Access Control
- The **system** decides based on fixed labels (Top Secret, Secret, Public)
- Users cannot change these rules
- Example: Military systems with clearance levels

### RBAC — Role-Based Access Control
- Access is based on your **role** (admin, editor, viewer)
- Most common model in web applications

### ABAC — Attribute-Based Access Control
- Access based on **multiple attributes** combined (who you are + time + location + resource type)
- Example: "Allow only if user is in Finance AND during business hours AND on the company network"

---

## Vulnerability Types

### 1. Unprotected Functionality
Admin panels or sensitive URLs with no access control at all.

- **Predictable URLs**: `/admin`, `/administrator`
- **Unpredictable URLs**: Hidden path leaked in JavaScript source code

**Key lesson**: Hiding a URL (security through obscurity) is NOT the same as securing it.

---

### 2. Platform Misconfiguration (Header Bypass)

The platform blocks access based on URL + HTTP method rules like:
```
DENY: POST, /admin/deleteUser, managers
```

**Bypass using headers:**
```
POST / HTTP/1.1
X-Original-URL: /admin/deleteUser
```

- Platform sees `/` → allows it
- App reads the header → routes to `/admin/deleteUser`
- The two layers disagree → bypass works

**Headers to try:**
- `X-Original-URL` — used by Drupal / reverse proxies
- `X-Rewrite-URL` — used by Microsoft IIS / .NET

---

### 3. HTTP Method Bypass

Platform blocks a specific method:
```
DENY: POST, /admin/deleteUser
```

Attacker tries the same URL with a different method:
```
GET /admin/deleteUser HTTP/1.1
```

The rule only blocks POST — GET slips through.

**Methods to try:** GET, POST, PUT, PATCH, HEAD

---

### 4. URL-Matching Discrepancies

The security layer and the application disagree on what URL they're looking at.

**Capitalization bypass:**
```
/ADMIN/DELETEUSER
/Admin/DeleteUser
```

**File extension bypass (Spring framework):**
```
/admin/deleteUser.json
/admin/deleteUser.anything
```
> Spring strips the extension and routes to the same endpoint. Works on Spring versions before 5.3 (useSuffixPatternMatch enabled by default).

**Trailing slash bypass:**
```
/admin/deleteUser/
```

---

### 5. Multi-Step Process Bypass

Apps implement rigorous checks on early steps but forget later ones.

Example:
```
Step 1: Load form       → access control ✅
Step 2: Submit changes  → access control ✅
Step 3: Confirm changes → NO access control ❌
```

**Attack**: Skip steps 1 and 2, send the step 3 request directly.

The dangerous assumption: "If they reached step 3, they must have passed earlier steps."
The server never actually verifies this.

---

### 6. IDOR — Insecure Direct Object Reference

When user-supplied input is used to access objects directly without authorization checks.

**Predictable IDs:**
```
/profile?id=1  → your profile
/profile?id=2  → someone else's profile (unauthorized)
```

**GUIDs** (Globally Unique Identifiers) are used to prevent guessing:
```
/profile?id=550e8400-e29b-41d4-a716-446655440000
```

But GUIDs fail if they are **leaked** anywhere in the app (page source, API responses, comments, Burp history).

---

## How to Prevent Access Control Vulnerabilities

| Principle | What it means |
|---|---|
| No obfuscation | Hiding ≠ Securing |
| Deny by default | Block everything, allow selectively |
| Single mechanism | One central security system, not many scattered checks |
| Declare at code level | Every resource must have explicit access rules |
| Audit regularly | Test it continuously or attackers will find it first |

**Defense in depth**: Assume attackers will find every URL, every endpoint, every parameter — and still can't get in.

---

## Labs Completed

> Tools used: Burp Suite (manual) + browser dev tools

| Lab | Difficulty | Vulnerability |
|---|---|---|
| Unprotected admin functionality with unpredictable URL | Apprentice | Admin path leaked in JS source |
| URL-based access control can be circumvented | Practitioner | X-Original-URL header bypass |
| Multi-step process bypass | Practitioner | Missing auth check on final step |
