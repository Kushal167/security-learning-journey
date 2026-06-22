# Authentication Vulnerabilities

## What is it
Exploiting flaws in how websites verify who you are —
bypassing logins, brute forcing credentials, and
manipulating session management.

## Labs Completed

### Lab 1 — Username Enumeration via Response Timing

#### How it works
Server takes longer to respond for valid usernames
because it actually checks the password hash.
Invalid usernames get rejected immediately.

#### Attack steps
1. Intercept login request in Burp
2. Add X-Forwarded-For header to bypass rate limiting
3. Send very long password to amplify timing difference
4. Use Pitchfork attack in Burp Intruder:
   - Position 1 → X-Forwarded-For value (increment)
   - Position 2 → username wordlist
5. Sort results by response time
6. Longest response = valid username

#### Key payload
```
X-Forwarded-For: 1.1.1.1
username=FUZZ&password=verylongpasswordhere
```

---

### Lab 2 — Username Enumeration via Account Lockout

#### How it works
Valid usernames trigger lockout message after 5 attempts.
Invalid usernames never get locked — different response!

#### Attack steps
1. Intercept login request in Burp
2. Send to Intruder → Cluster Bomb attack
3. Position 1 → username wordlist
4. Position 2 → null payloads (generate 5)
5. Add grep match → "too many"
6. Valid username gets checkmark in results

#### Fix for Burp Community throttling — use ffuf
```bash
ffuf.exe -w usernames.txt -X POST
-d "username=FUZZ&password=test"
-H "Content-Type: application/x-www-form-urlencoded"
-H "Cookie: session=YOUR_SESSION"
-u https://LAB-URL/login
-mr "too many" -t 1
```

---

### Lab 3 — 2FA Broken Logic

#### How it works
Server doesn't verify same user completes both login steps.
Cookie swap tricks server into completing 2FA as victim.

#### The flaw
```
Step 1 → login sets cookie: verify=wiener
Step 2 → server trusts verify cookie blindly
         change verify=carlos → server thinks carlos is logging in
```

#### Attack steps
1. Login as wiener:peter
2. Change verify cookie → verify=carlos
3. GET /login2 → generates OTP for carlos
4. Brute force OTP 0000-9999 using Python script

---

### Lab 4 — Brute Forcing Stay Logged In Cookie

#### How it works
Stay logged in cookie constructed as:
```
base64(username:md5(password))
```

#### Attack steps
1. Login with stay logged in → inspect cookie
2. Decode base64 → see username:md5hash format
3. For each password in wordlist:
   - MD5 hash the password
   - Build: carlos:md5hash
   - Base64 encode
   - Try as stay-logged-in cookie
4. Look for "Update email" in response = valid!

#### Burp Intruder payload processing rules
```
1. Hash: MD5
2. Add prefix: carlos:
3. Encode: Base64-encode
4. Uncheck URL encode
```

---

### Lab 5 — Password Reset Poisoning

#### How it works
Server builds reset URL using Host header.
Attacker changes Host header to their server.
Victim clicks poisoned link → token goes to attacker.

#### Attack steps
1. Request password reset for carlos
2. Intercept in Burp → change Host header:
```
Host: YOUR-EXPLOIT-SERVER.com
```
3. Carlos gets email with poisoned link
4. Check exploit server logs → copy token
5. Use token on real website → reset password

---

## Key concepts

### X-Forwarded-For spoofing
```
Server rate limits by IP
Add: X-Forwarded-For: 1.1.1.1
Change per request → server sees different IP
Never triggers rate limit!
```

### MD5 hashing
```
One way function — cannot be reversed
password → 5f4dcc3b5aa765d61d8327deb882cf99
Crack with crackstation.net
```

### Base64 encoding
```
NOT encryption — easily decoded!
wiener:password → d2llbmVyOnBhc3N3b3Jk
Decode at base64decode.org
```

### Burp attack types
| Type | Use case |
|---|---|
| Sniper | Single payload position |
| Battering Ram | Same payload everywhere |
| Pitchfork | Paired lists in sync |
| Cluster Bomb | Every combination |

## Tools used
- Burp Suite Intruder (Sniper, Pitchfork, Cluster Bomb)
- Turbo Intruder
- ffuf
- Python requests + concurrent.futures

## Scripts written
- find_user.py → username enumeration
- brute_2fa.py → 2FA OTP brute force

## Labs skipped
- Out of band labs → require Burp Pro
