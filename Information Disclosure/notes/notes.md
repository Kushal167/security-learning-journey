# Information Disclosure Vulnerabilities — Notes
> PortSwigger Web Security Academy

---

## What is Information Disclosure?

When a web application unintentionally reveals sensitive information to users. This includes internal data, technical details, credentials, or anything that gives an attacker an advantage.

---

## 1. Files for Web Crawlers

### What it is
Websites provide `/robots.txt` and `/sitemap.xml` to guide web crawlers (bots like Google).

### Why it's dangerous
- `robots.txt` lists directories crawlers should SKIP — accidentally giving attackers a map of sensitive areas
- `sitemap.xml` lists all pages — may reveal forgotten or sensitive endpoints
- These files are NOT linked from the website so Burp won't find them automatically

### Key Point
Crawlers obey these files. Attackers do not.

### How to find
Manually visit:
```
https://target.com/robots.txt
https://target.com/sitemap.xml
```

---

## 2. Error Messages

### What it is
Verbose error messages that reveal more information than they should.

### What errors can reveal
- What input/data type a parameter expects (helps narrow attacks)
- Technology stack (framework, database, server)
- Exact version numbers (leads to CVE lookup)
- Internal file paths
- Open source framework (allows source code study)
- Different errors = different behavior (SQL injection, username enumeration)

### Types of errors and what they leak
| Error Message | What You Learn |
|---|---|
| `PHP Fatal error on line 23` | Server runs PHP |
| `MySQLSyntaxErrorException` | Database is MySQL |
| `Whitelabel Error Page - Spring Boot` | Java Spring framework |
| `TemplateNotFound: Jinja2` | Uses Jinja2 template engine |
| `Apache Tomcat/9.0.37` | Exact server + version |

### Key Point
Different errors for different inputs = different behavior happening behind the scenes. This is crucial for SQL injection and username enumeration.

### How to trigger errors
- Put letters in numeric fields
- Add `'` or `"` to any input
- Send negative numbers (`-1`, `99999999`)
- Remove required parameters
- Send wrong HTTP method
- Send huge input (10,000 characters)

---

## 3. Debugging Data

### What it is
Debug messages and logs left enabled on production servers that were meant only for development.

### What debug data can contain
- Session variable values that can be manipulated
- Hostnames and credentials for backend components
- File and directory names on the server
- Keys used to encrypt data
- Full application runtime state (in log files)

### Why it's dangerous
A single debug page can give you everything needed for a complete attack — credentials, keys, paths, session data — all in one place.

### Common debug endpoints to check
```
/console
/debug
/trace
/phpinfo.php
/actuator          (Spring Boot)
/actuator/env      (leaks everything)
/actuator/health
/actuator/mappings
/_profiler         (Symfony)
/app_dev.php       (Symfony dev mode)
```

### Common log file locations
```
/debug.log
/app.log
/error.log
/logs/debug.txt
/application/logs/
/var/log/apache2/error.log
/var/log/nginx/error.log
```

---

## 4. User Account Pages

### What it is
Account pages hold sensitive data. Logic flaws can allow attackers to view other users' data by tampering with parameters.

### How it works
Site loads account page based on URL parameter:
```
GET /user/personal-info?user=carlos
```
If the app doesn't verify the logged-in user matches the parameter — change it to see anyone's data.

### Key Point
The app might protect the full account page but forget to protect individual data endpoints:
```
/user/account?user=victim        ← Blocked ✅
/user/api-key?user=victim        ← Not protected ❌
/user/address?user=victim        ← Not protected ❌
```

### This is called
**IDOR — Insecure Direct Object Reference**

### Parameters to look for and tamper
```
?user=yourname
?id=1234
?account=carlos
?userId=42
```

---

## 5. Source Code Disclosure via Backup Files

### What it is
Text editors create temporary backup files automatically. If these are left on the server, attackers can read the actual source code.

### Why normal requests don't work
When you request `login.php` the server executes it and returns HTML. You never see the code.

### Why backup files work
The server doesn't know how to execute `.bak` or `.php~` files — so it returns them as plain text, exposing the source code.

### Backup file extensions by editor
| Editor | Original File | Backup File |
|---|---|---|
| Vim | login.php | login.php~ |
| Emacs | login.php | #login.php# |
| Generic | login.php | login.php.bak |
| Generic | login.php | login.php.old |
| Generic | login.php | login.copy.php |

### What source code can contain
- Hardcoded database credentials
- API keys
- Secret encryption keys
- Internal logic that reveals injection points

---

## 6. Insecure Configuration

### What it is
Vulnerabilities from improper server/application settings — not bad code, but bad configuration.

### Two main causes
1. Complex third-party technologies with settings not fully understood
2. Debug settings left enabled in production

### HTTP TRACE Method
TRACE is a diagnostic method — it echoes back the exact request the server received, including headers added by reverse proxies.

**How it works:**
```
You → Reverse Proxy (adds secret headers) → Web Server
                                                 ↓
                              TRACE echoes everything back
                                                 ↓
                         You see secret internal headers
```

**TRACE is a server-level setting:**
- Either enabled for the whole server or disabled entirely
- Test once on `/` — if it works anywhere, it works everywhere
- `200 OK` = enabled, `405 Method Not Allowed` = disabled

### Other common misconfigurations
| Misconfiguration | What it Exposes |
|---|---|
| TRACE enabled | Internal headers, auth tokens |
| Directory listing on | All files in folder visible |
| Default credentials | Admin panels with admin/admin |
| Swagger UI exposed | All API endpoints |
| `/actuator` exposed | Full Spring Boot internals |
| phpinfo() page up | Full server configuration |
| `.env` file accessible | All environment variables |

---

## 7. Version Control History (Git)

### What it is
Developers use Git to track code changes. The `.git` folder stores the entire history. If left on a production server, attackers can access all historical code — including deleted secrets.

### Why it's dangerous
Git never forgets. Even if a password was deleted 6 months ago, it still exists in the commit history.

### What you can find
- Commit logs with history of every change
- Deleted lines containing old credentials
- Developer names and internal email addresses
- Commit messages hinting at vulnerabilities
- Hardcoded secrets from old commits

### How to check if exposed
```
GET /.git/HEAD
```
Response: `ref: refs/heads/master` = EXPOSED

### Key files to request manually
```
/.git/HEAD
/.git/config
/.git/COMMIT_EDITMSG
/.git/logs/HEAD
/.git/info/excludes
```

### How to download and read
```bash
# Download
python -m git_dumper https://target.com/.git/ gitfiles

# Navigate into folder
cd gitfiles

# See all commits
git log

# See what changed in a specific commit
git show <commit_id>
```

### What to look for in git show output
- Lines starting with `-` (red) = deleted lines = where secrets were
- Lines starting with `+` (green) = new replacement code

---

## Summary Table

| Type | What Leaks | How to Find |
|---|---|---|
| robots.txt / sitemap | Hidden paths & directories | Manually visit `/robots.txt` |
| Error Messages | Tech stack, versions, DB type | Trigger errors with bad input |
| Debug Data | Credentials, keys, session data | Visit `/console`, `/phpinfo.php` |
| Account Pages | Other users' personal data | Tamper user parameter in Repeater |
| Backup Files | Source code, hardcoded secrets | Try `.bak` `~` `.old` in Repeater |
| Insecure Config | Internal headers, auth tokens | Send `TRACE` request in Repeater |
| Version Control | Full history, deleted secrets | Visit `/.git/HEAD` in Repeater |

---

## Tools Used (Community Edition Friendly)

- **Burp Suite Community** — Proxy, Repeater, Intruder
- **Git Bash** — curl, git commands
- **git-dumper** — download exposed .git folders
- **Browser** — manual navigation, page source inspection
