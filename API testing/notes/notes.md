# API Testing — Notes
> PortSwigger Web Security Academy

---

## What is an API?

An API is how two systems talk to each other behind the scenes. When you log in, click a button, or submit a form — there's an API carrying that request to the server and bringing back a response.

Think of it like a waiter in a restaurant — you tell the waiter what you want, the waiter goes to the kitchen, and brings back your order. The kitchen (server) never talks to you directly.

---

## 1. Identifying API Endpoints

- Use **Burp Scanner** to crawl the application and auto-detect endpoints
- Browse manually too — some endpoints only appear when you perform specific actions (login, checkout, etc.)
- Look for URL patterns like `/api/`, `/v1/`, `/graphql/`, `/rest/`
- Dig into **JavaScript files** — developers often hardcode API endpoint paths inside them
- Use the **JS Link Finder** BApp for deeper extraction from JS files
- Don't fully trust API docs — they can be outdated or inaccurate

---

## 2. Interacting with API Endpoints

- Use **Burp Repeater** to manually modify and resend requests one at a time
- Use **Burp Intruder** to automate sending many variations of a request
- Try changing the **HTTP method** (GET → POST → PUT → DELETE) — servers often misconfigure method-level access
- Try changing the **Content-Type header** — different formats go through different code paths
- Read **error messages carefully** — they often leak field names, formats, and internal structure

---

## 3. Identifying Supported Content Types

- Modify the `Content-Type` header and reformat the body to match
- Switching formats can:
  - Trigger errors that disclose useful information
  - Bypass security filters (e.g. WAF only scans JSON, not XML)
  - Hit different, less-secure code paths (e.g. JSON is secure but XML has XXE)
- Use the **Content Type Converter** BApp to automatically convert between JSON and XML
- Common content types to try: `application/json`, `application/xml`, `application/x-www-form-urlencoded`, `multipart/form-data`

---

## 4. Mass Assignment Vulnerabilities

- Occurs when frameworks automatically bind ALL request fields to a database object
- Developers intend only certain fields to be editable — but the framework doesn't enforce this automatically
- Hidden fields like `isAdmin`, `role`, `balance` exist on the object but aren't exposed in the UI
- The framework blindly applies whatever fields you send — including ones you were never meant to touch

### How to Find Hidden Fields

- **Read GET responses** — servers often return the full internal object including fields never shown in the UI
- **Check JavaScript files** — developers reference field names inside app logic files sent to your browser
- **Trigger error messages** — broken input can make the server accidentally reveal expected field names
- **Find API documentation** — `/openapi.json`, `/swagger.json` etc. list every field in the system
- **Guess common names** — `isAdmin`, `role`, `verified`, `balance`, `accessLevel`, `status`, `permissions`

### The Process
```
Step 1 → Read GET responses        (what fields exist?)
Step 2 → Check JavaScript files    (what fields are referenced?)
Step 3 → Trigger error messages    (what fields does the server mention?)
Step 4 → Find API documentation    (is there a full blueprint?)
Step 5 → Guess common names        (try isAdmin, role, verified etc.)
```

---

## 5. Server-Side Parameter Pollution (SSPP)

Occurs when user input is embedded into a server-side request to an internal API without proper sanitization. You inject special characters to manipulate the internal request structure.

```
You → [Website Server] → [Internal API]
                ↑
         this part is hidden
```

Can be tested in: query parameters, form fields, headers, and URL path parameters.

### Truncation with `#` (`%23`)
- `#` cuts off everything after it in a URL
- Use `%23` (URL-encoded) so the front-end passes it through instead of stripping it
- Chops off security conditions that come after it in the internal request

```
Input:    administrator%23foo
Internal: /users/search?name=administrator#foo&publicProfile=true
Result:   publicProfile=true gets ignored — security condition removed
```

### Injecting Parameters with `&` (`%26`)
- `&` separates parameters in a URL
- Use `%26` to inject a new parameter into the internal request
- Start with a fake parameter (`foo=xyz`) to confirm injection works, then try real names

```
Input:    peter%26foo=xyz
Internal: /users/search?name=peter&foo=xyz&publicProfile=true
Result:   if response unchanged, injection is confirmed
```

### Overriding Existing Parameters
- Inject the same parameter name twice to try and overwrite its value
- Behaviour depends on backend technology:
  - **PHP** → last value wins
  - **ASP.NET** → combines both values (e.g. `peter,carlos`)
  - **Node.js/Express** → first value wins

```
Input:    peter%26name=carlos
Internal: /users/search?name=peter&name=carlos
PHP result: searches for carlos
```

### Path Traversal in API URLs
- `..` means "go back one level" — works in URL paths just like navigating folders
- Can navigate away from your intended endpoint to a restricted one

```
/api/users/peter/../admin  →  resolves to  →  /api/users/admin
```

### Structured Format Injection (JSON)
- Instead of injecting into query strings, inject into JSON body data
- Inserting `"` breaks out of a JSON field and adds new fields
- When input is already JSON, use escaped quotes `\"` to smuggle the injection past the browser

**Plain text input → JSON (use raw quotes):**
```
Input:    peter","access_level":"administrator
Result:   {"name":"peter","access_level":"administrator"}
```

**JSON input → JSON (use escaped quotes):**
```
Input:    {"name": "peter\",\"access_level\":\"administrator"}
Decoded:  {"name":"peter","access_level":"administrator"}
```

The `\` backslashes hide the quotes from your browser so they pass through safely as plain text. When the server decodes them, they become real `"` characters that break out of the JSON field.

---

## 6. Preventing API Vulnerabilities

- Secure and restrict access to API documentation if not public
- Keep documentation up to date so testers have full visibility
- Apply an **allowlist** of permitted HTTP methods per endpoint
- Validate that content types match what is expected
- Use **generic error messages** — never leak field names, table names, or stack traces
- Apply security measures to **all API versions**, not just the current one
- For mass assignment: use an **allowlist** of fields users can update (safer than a blocklist)

---

## 7. Expert Lab — Password Reset Token Takeover

### What Happened
The `username` parameter in a password reset form was being placed directly into a URL path on the server side without sanitization. By using path traversal and the API structure discovered via `openapi.json`, it was possible to retrieve the administrator's password reset token directly.

### Why `../../v1/` Was Needed
The application was running a version of the API that didn't support `passwordResetToken`. Using `../../` navigated back out of the current version's path, then `/v1/` manually specified the correct version that did support it.

```
Current (wrong):  /api/internal/v2/users/administrator/field/passwordResetToken
Fixed:            /api/internal/v1/users/administrator/field/passwordResetToken
                                    ↑
                       ../../v1/ navigates here manually
```

### Full Attack Chain
```
1. Capture POST /forgot-password in Burp Repeater
2. Probe username parameter with special characters to confirm URL path injection
3. Use ../ sequences incrementally until "Not found" (outside API root)
4. Request openapi.json to get the internal API blueprint
5. Use discovered endpoint structure to navigate to passwordResetToken field
6. Use ../../v1/ to switch to the API version that supports passwordResetToken
7. Retrieve the reset token from the response
8. Visit /forgot-password?passwordResetToken=TOKEN and reset the password
9. Log in as administrator and delete carlos
```

---

## 8. Automated Testing Tools

- **Burp Scanner** — auto-detects suspicious input transformations during audits; findings need manual follow-up
- **Backslash Powered Scanner BApp** — classifies inputs as boring, interesting, or vulnerable; investigate interesting ones manually
- Automated tools are a first filter — they narrow down what to test manually, not a replacement for manual testing

---

## Real World Impact Summary

| Attack | Business Impact |
|---|---|
| Mass Assignment | Attacker grants themselves admin access |
| Parameter Pollution | Attacker accesses other users' private data |
| Path Traversal | Attacker retrieves password reset tokens and takes over accounts |
| Content Type Switching | Attacker bypasses security filters entirely |
| Structured Format Injection | Attacker elevates privileges via JSON/XML body manipulation |
