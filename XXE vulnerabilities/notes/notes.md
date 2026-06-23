# XXE Injection - Notes

## What is XXE?
XML External Entity injection. You trick the server's XML parser into fetching external resources (files, URLs) by defining malicious entities in the DOCTYPE. The parser does the work — the XML itself is just passive instructions.

---

## Core Concepts

### XML Entity Basics
- **Entity** → a variable/placeholder in XML
- **`SYSTEM`** → marks it as external (fetched from outside the document)
- **`&entityname;`** → where the fetched content gets substituted
- Entity name is **completely arbitrary** — call it anything (`ext`, `xxe`, `foo`, `abc`)
- The name in the definition and the reference **must match**

### DOCTYPE
- `<!DOCTYPE foo [...]>` → declares the document type and internal subset
- `foo` is just a throwaway placeholder name — doesn't matter
- Supposed to match the root element but parsers rarely enforce this

### Parameter Entities vs Regular Entities
| | Regular Entity | Parameter Entity |
|---|---|---|
| Symbol | `&name;` | `%name;` |
| Used in | XML content | DTD definitions only |
| Purpose | Insert data | Insert DTD code |

---

## Attack Surface

### Obvious Attack Surface
- HTTP requests with `Content-Type: application/xml` or `text/xml`
- Any form/API that sends XML data

### Hidden Attack Surface
- **File uploads** → SVG, DOCX, XLSX, PPTX are secretly XML-based
- **XInclude** → when you only control part of an XML document
- **SOAP requests** → backend may embed your data into XML

---

## Attack Types

### 1. Classic XXE (Inband)
You control the full XML document. Output is reflected back in the response.

### 2. XInclude Attack
Used when you only control a small piece of data embedded into a larger XML document (e.g. SOAP). You can't touch the DOCTYPE so you use XInclude instead.

### 3. SVG File Upload XXE
App accepts image uploads → library also supports SVG → SVG is XML → you sneak XXE inside.

### 4. Blind XXE (Outband)
No output in response. Use out-of-band callbacks (DNS/HTTP) to confirm vulnerability and exfiltrate data.

### 5. Error-Based XXE
Force the parser to throw an error that leaks file contents in the error message.

### 6. Local DTD XXE
Last resort when both inband and outband are blocked. Repurpose an existing DTD file on the server to trigger error-based data leakage.

---

## Priority Order
```
Inband XXE        → easiest, try first
Outband XXE       → if inband blocked
Error-based       → if outband blocked
Local DTD         → absolute last resort
```

---

## Cloud Metadata Endpoints
When the app is hosted in the cloud, target the metadata service instead of local files.

| Cloud | URL |
|---|---|
| AWS | `http://169.254.169.254/latest/meta-data/` |
| AWS IAM Creds | `http://169.254.169.254/latest/meta-data/iam/security-credentials/` |
| GCP | `http://metadata.google.internal/computeMetadata/v1/` |
| Azure | `http://169.254.169.254/metadata/instance?api-version=2021-02-01` |

`169.254.169.254` is a link-local address reserved across all major cloud providers — only reachable from within the instance itself, making SSRF/XXE especially dangerous here.

---

## Confirming XXE Vulnerability

**Step 1:** Test if entities are processed at all
```xml
<!DOCTYPE foo [ <!ENTITY test "hello123"> ]>
<data>&test;</data>
```
If response contains `hello123` → parser processes entities ✅

**Step 2:** Try file retrieval
```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///etc/hostname"> ]>
<data>&ext;</data>
```
If hostname appears in response → confirmed vulnerable 🎯

**Step 3:** If no output → try blind XXE (Burp Collaborator callback)

**Signs of vulnerability:**
- Entity value reflected in response
- File contents in response
- Error messages revealing file paths
- Out-of-band DNS/HTTP callbacks

---

## If Both Inband and Outband Fail
- Try different file paths (`/etc/hosts`, `/proc/self/environ`, `/proc/version`)
- Try error-based XXE (point to a nonexistent file)
- Try XInclude
- Check ALL parts of the response (headers, hidden fields, HTML comments)
- If everything fails → app is likely not vulnerable, move on

---

## XML Escape Sequences
XML has reserved characters. Encode payloads to avoid breaking syntax and bypass weak filters:

| Character | Encoded |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `'` | `&apos;` |
| `"` | `&quot;` |
| `%` | `&#x25;` |

---

## Override vs Overwrite
- **Override** → replace something while the original still exists (original DTD file untouched on disk)
- **Overwrite** → permanently destroy and replace the original

In XXE we **override** entities — we redefine them in our DOCTYPE before the DTD loads. The parser sees ours first.

---

## Local DTD — Key Concepts
- A DTD file that already exists on the server filesystem
- Used as last resort when all other methods are blocked
- You find a **parameter entity** (`%`) inside the DTD that you can override
- Known working pairs:

| DTD | Entity to Override |
|---|---|
| `/usr/share/yelp/dtd/docbookx.dtd` | `ISOamso` |
| `/usr/share/xml/fontconfig/fonts.dtd` | `expr` |

**How to find which entity to override:**
1. Use XXE to read the DTD file first
2. Look for parameter entities (`<!ENTITY % name ...>`)
3. Pick one that won't crash the DTD when overridden
4. Or reference PortSwigger/cheat sheets for known pairs

---

## w3.org Namespaces
URLs like `http://www.w3.org/2000/svg` are **namespace identifiers**, not actual network requests. They're just labels telling the parser which standard to follow. W3C (World Wide Web Consortium) is the organization that defines web standards (HTML, XML, SVG, CSS etc.).

---

## XML vs Script
XML/SVG markup is NOT a script. It has no logic, loops, or functions. It's passive structured data. The "action" is performed by the **server's XML parser** when it processes the file — not by the XML itself.

---

*Notes based on PortSwigger Web Security Academy XXE module. Reference payloads sourced from GoSecure's GitHub repository.*
