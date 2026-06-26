# API Testing — Cheatsheet
> PortSwigger Web Security Academy

---

## Endpoint Discovery

| Method | What To Do |
|---|---|
| Burp Scanner | Crawl the app automatically |
| Manual browsing | Click through the app in Burp's browser |
| URL patterns | Look for `/api/`, `/v1/`, `/graphql/`, `/rest/` |
| JS files | Hunt for hardcoded endpoint paths |
| JS Link Finder BApp | Deep extraction of endpoints from JS files |
| API docs | Use as a hint — verify manually, may be outdated |

---

## HTTP Methods to Try

| Method | Purpose |
|---|---|
| `GET` | Fetch data |
| `POST` | Create something |
| `PUT` | Replace/update something |
| `PATCH` | Partially update something |
| `DELETE` | Remove something |
| `OPTIONS` | See what methods are allowed |
| `HEAD` | Like GET but no response body |

---

## Content Types to Try

| Content-Type | Format Example |
|---|---|
| `application/json` | `{"user":"admin"}` |
| `application/xml` | `<user>admin</user>` |
| `application/x-www-form-urlencoded` | `user=admin` |
| `multipart/form-data` | File uploads |

---

## Finding Hidden Fields

| Method | What To Do |
|---|---|
| GET response | Read full response — note every field returned |
| JavaScript files | Search for field names referenced in app logic |
| Error messages | Send broken input — server may reveal field names |
| API documentation | Check `/openapi.json`, `/swagger.json`, `/api-docs` |
| Common name guessing | Try `isAdmin`, `role`, `verified`, `balance`, `accessLevel` |

---

## Mass Assignment

| Step | What To Do |
|---|---|
| 1 | Send a GET request and read the full response object |
| 2 | Note any fields not exposed in the UI |
| 3 | Add those fields to a POST/PATCH request body |
| 4 | Check if the server accepted and applied them |

---

## SSPP — Special Characters

| Character | Encoded | Purpose |
|---|---|---|
| `#` | `%23` | Truncate — cut off everything after this point |
| `&` | `%26` | Inject — add a new parameter |
| `=` | `%3D` | Assign — manipulate parameter values |
| `?` | `%3F` | Test — signals start of query string, truncates path |

---

## Override Behaviour by Technology

| Technology | Duplicate Param Behaviour | Result |
|---|---|---|
| PHP | Last value wins | `admin` |
| ASP.NET | Combines both | `peter,admin` → likely error |
| Node.js/Express | First value wins | `peter` unchanged |

---

## Path Traversal Quick Reference

```
./     = stay in same directory
../    = go back one level
../../ = go back two levels
```

---

## Diagnostic Response Guide

| Response | Meaning |
|---|---|
| `Invalid route` | Input is in a URL path — truncation/traversal is working |
| `Not found` | You've navigated outside the API root |
| `Invalid name` | Injection didn't work — string treated as literal input |
| Unchanged response | Injection worked but parameter ignored — try real param names |
| Different data returned | Injection worked and affected output |
| Error with field names | Server leaked internal structure — note the field names |

---

## JSON Injection — Quote Rules

| Situation | What to Use | Why |
|---|---|---|
| Plain text input → JSON | Raw `"` | Browser sends plain text, server wraps in JSON |
| JSON input → JSON | Escaped `\"` | Must hide quotes from browser before server decodes them |

---

## Common API Documentation Paths

```
/openapi.json
/openapi.yaml
/swagger.json
/swagger.yaml
/api/docs
/api-docs
/v1/swagger.json
/v2/api-docs
/docs
```

---

## Prevention Checklist (Defender)

- [ ] Restrict access to API documentation
- [ ] Keep documentation up to date
- [ ] Allowlist permitted HTTP methods per endpoint
- [ ] Validate Content-Type on every request
- [ ] Use generic error messages only
- [ ] Apply security to all API versions including old ones
- [ ] Allowlist fields users can update (not blocklist)
