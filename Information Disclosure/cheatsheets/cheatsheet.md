# Information Disclosure — Cheat Sheet
> Quick reference for PortSwigger Labs & Real World Testing

---

## 🔍 First Things to Always Check

```
1. /robots.txt
2. /sitemap.xml
3. Page source (Ctrl+U) — look for comments
4. Response headers in Burp — look for Server, X-Powered-By
5. /.git/HEAD
6. /phpinfo.php
7. /.env
```

---

## 🗺️ robots.txt & sitemap.xml

```
Target: https://target.com

Manual visit:
→ https://target.com/robots.txt
→ https://target.com/sitemap.xml

Note every path listed → visit each one in Burp Repeater
```

---

## 💥 Triggering Error Messages

| What to Do | How |
|---|---|
| Wrong data type | Put `abc` in a numeric ID field |
| SQL characters | Add `'` `"` `--` to any input |
| Empty required fields | Delete parameter values in Repeater |
| Huge input | Paste 10,000 characters |
| Wrong format | Send XML where JSON expected |
| Negative numbers | Send ID = `-1` or `99999999` |
| Wrong HTTP method | Send `DELETE` instead of `GET` |

---

## 🐛 Debug Endpoints to Check

```
/console
/debug
/trace
/phpinfo.php
/actuator
/actuator/env
/actuator/health
/actuator/mappings
/actuator/beans
/_profiler
/app_dev.php
/server-status
/server-info
```

---

## 📁 Log File Locations

```
/debug.log
/app.log
/error.log
/logs/debug.txt
/logs/error.txt
/application/logs/
/tmp/debug.log
/var/log/apache2/error.log
/var/log/nginx/error.log
```

---

## 🗂️ Backup File Extensions to Try

```
Original: /login.php

Try:
/login.php~
/login.php.bak
/login.php.old
/login.php.orig
/login.php.swp
/.login.php.swp
/login.bak
/login.old
/login.copy.php
/#login.php#
/login.php.temp
/login.php_bak
/login.php.1
```

---

## 🔧 HTTP TRACE Test

In Burp Repeater:
```
TRACE / HTTP/1.1
Host: target.com
```

| Response | Meaning |
|---|---|
| `200 OK` + request echoed | TRACE enabled — look for leaked headers |
| `405 Method Not Allowed` | TRACE disabled — move on |
| `403 Forbidden` | Blocked by WAF — may still be enabled underneath |

---

## 👤 User Account Parameter Tampering (IDOR)

```
Original request:
GET /user/personal-info?user=yourname

Change to:
GET /user/personal-info?user=admin
GET /user/personal-info?user=carlos
GET /user/personal-info?user=wiener
GET /user/personal-info?id=1
GET /user/personal-info?id=2
GET /user/personal-info?id=0
GET /user/personal-info?id=-1
```

Compare responses — different data = vulnerability found.

---

## 🔑 Git Exposure Check

```
Step 1 — Check if exposed:
GET /.git/HEAD
→ Response: "ref: refs/heads/master" = EXPOSED ✅

Step 2 — Key files to grab manually:
/.git/HEAD
/.git/config
/.git/COMMIT_EDITMSG
/.git/logs/HEAD
/.git/info/excludes
/.git/packed-refs
```

---

## 🌐 Technology Fingerprinting

| What You See | Technology |
|---|---|
| `X-Powered-By: PHP/7.4` | PHP |
| `JSESSIONID` cookie | Java |
| `PHPSESSID` cookie | PHP |
| `ASP.NET_SessionId` cookie | ASP.NET |
| `Whitelabel Error Page` | Spring Boot |
| `Server: Apache` | Apache |
| `Server: nginx` | Nginx |
| `X-AspNet-Version` header | ASP.NET |

---

## 🔎 Google Dorking (Passive Recon)

```
site:target.com ext:bak
site:target.com ext:env
site:target.com ext:log
site:target.com "index of"
site:target.com inurl:backup
site:target.com "wp-config"
site:target.com ext:sql
site:target.com ext:conf
```

---

## 📊 Severity Quick Reference

| Finding | Severity |
|---|---|
| Credentials in error message | Critical |
| Encryption key exposed | Critical |
| Git history with secrets | High |
| Database error with query | High |
| Source code via backup file | High |
| Debug page exposed | High |
| Stack trace / file paths | Medium |
| Version number disclosure | Medium |
| robots.txt sensitive paths | Low-Medium |
| Generic stack trace | Low |

---

## ⚡ Burp Suite Community Workflow

```
1. Open lab → Add to scope in Target tab
2. Browse site → Check Proxy HTTP History
3. Manually visit robots.txt, sitemap.xml
4. Check page source for comments
5. Check response headers for tech info
6. Send interesting requests to Repeater
7. Tamper inputs to trigger errors
8. Try backup extensions on discovered files
9. Send TRACE request
10. Check /.git/HEAD
```
