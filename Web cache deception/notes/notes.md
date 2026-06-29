# Web Cache Deception — Notes

## What is Web Cache Deception?

An attack where an attacker tricks a web cache into storing sensitive, user-specific content and then retrieves it themselves.

The cache sits between the user and server. It stores static resources and serves them to future visitors without hitting the origin server. The attack exploits a **mismatch** between how the cache and origin server interpret a URL.

---

## How Caching Works

- Cache stores responses for static resources (images, CSS, JS)
- Cache decides what to store based on URL, file extension, or path patterns
- Dynamic content is NOT cached as it may contain sensitive data

---

## Cache Rules

### 1. Static File Extension Rules
Match the file extension of the requested resource:
```
/style.css   → cache it
/app.js      → cache it
/image.png   → cache it
/dashboard   → don't cache
```

### 2. Static Directory Rules
Match all URL paths that start with a specific prefix:
```
/static/logo.png   → cache it
/assets/style.css  → cache it
/account/profile   → don't cache
```

### 3. File Name Rules
Match specific well-known file names:
```
/robots.txt    → cache it
/favicon.ico   → cache it
/sitemap.xml   → cache it
```

---

## Attack Flow

```
1. Attacker crafts malicious URL
2. Victim visits URL while logged in
3. Server returns victim's private data
4. Cache stores it thinking it's a static file
5. Attacker fetches same URL
6. Cache serves attacker the victim's private data
```

---

## What Can Be Stolen

- API keys
- Session tokens
- Personal information (email, address)
- CSRF tokens
- Any user-specific data in HTML responses

---

## Cache Buster

A unique query string added to every request so the cache always treats it as a brand new request:
```
/profile?cb=1    → fresh request
/profile?cb=2    → fresh request
/profile?cb=3    → fresh request
```

Use **Param Miner** extension in Burp to automate this:
```
Param Miner → Settings → Add dynamic cachebuster
```

Always use a cache buster while testing so results reflect what the server is doing, not what the cache has stored.

---

## Types of Discrepancies

### 1. Path Mapping Discrepancy
Server ignores extra path segments, cache sees the extension:
```
/my-account/foo.js
Server reads: /my-account      → returns private data
Cache reads:  /my-account/foo.js → sees .js → caches it
```

### 2. Delimiter Discrepancy
Server and cache use different characters as delimiters:
```
/my-account;foo.js
Server reads: /my-account (stops at ;)  → returns private data
Cache reads:  /my-account;foo.js → sees .js → caches it
```

### 3. Delimiter Decoding Discrepancy
Server and cache decode encoded characters differently:

**Example 1 — %23 (#)**
```
/profile%23wcd.css
Server: decodes %23 → # → stops → reads /profile → returns private data
Cache:  doesn't decode %23 → sees .css → caches it
```

**Example 2 — %3f (?)**
```
/myaccount%3fwcd.css
Cache:  checks rules BEFORE decoding → sees .css → decides to cache
        then decodes %3f → ? → forwards /myaccount?wcd.css to server
Server: receives decoded URL → sees ? → stops → reads /myaccount → returns private data
```

### 4. Static Directory Discrepancy (Server Normalizes)
Server resolves path traversal, cache doesn't:
```
/resources/..%2fmy-account
Server: resolves to /my-account → returns private data
Cache:  sees /resources prefix → caches it
```

### 5. Static Directory Discrepancy (Cache Normalizes)
Cache resolves path traversal, server doesn't. Requires combining with a delimiter:
```
/my-account;%2f%2e%2e%2fstatic
Cache:  doesn't know ; → reads full path → resolves to /static → caches it
Server: sees ; → stops → reads /my-account → returns private data
```

---

## X-Cache Headers

| Header | Meaning |
|---|---|
| `X-Cache: miss` | Cache went to server, got fresh response, stored it |
| `X-Cache: hit` | Cache served a stored response |
| No cache header | Cache didn't store anything |

**miss → hit = cache stored the response = discrepancy confirmed**

---

## Normalization

Normalization is when a server cleans up and simplifies a URL before processing it:
```
/aaa/../profile  →  normalizes to  →  /profile
```

### Testing Origin Server Normalization
```
Send: /aaa/..%2fmy-account

Same response as /my-account? → server normalizes ✅
404?                          → server doesn't normalize ❌
```

Use a POST request for testing — caches don't store POST responses so results are reliable.

### Testing Cache Normalization
```
Send: /aaa/..%2fresources/js/file.js

No longer cached? → cache doesn't normalize ✅ (good for attack)
Still cached?     → cache normalizes ❌
```

Confirm cache rule is prefix based:
```
Send: /resources/aaa (no extension, random path)

X-Cache: miss then hit? → confirms prefix rule ✅
```

---

## Defenses

- Set `Cache-Control: no-store` on all authenticated/dynamic responses
- Configure cache to never cache responses based on extension alone
- Ensure cache and server agree on URL normalization
- Use `Vary` headers appropriately
