# Custom Reconnaissance Tool — Complete Development Plan

## 1. Project Overview

Build a lightweight, modular, CLI-based reconnaissance tool written in **Python**.

The tool is intended for authorized penetration testing, security assessments, educational labs, and systems where the user has permission to perform reconnaissance.

The final project will contain **6 independent modules**, each developed in its own Git branch and eventually merged into `main`.

The final application must run from `main` after all branches have been completed and merged.

---

# 2. Repository

This is a **new GitHub repository**.

The initial repository should contain the project documentation and basic project structure.

Recommended initial files:

```text
recon-tool/
│
├── plan.md
├── README.md
├── .gitignore
└── requirements.txt
```

The implementation can create additional folders/files as required.

---

# 3. Branch Architecture

The project will use exactly these feature branches:

```text
main
│
├── feature/whois-dns
├── feature/subdomain
├── feature/port-scanner
├── feature/banner-tech
├── feature/reporting
└── feature/cli-logging
```

Each feature branch is responsible for one major part of the application.

The branches will eventually be merged into `main`.

---

# 4. Development Order

The modules MUST be developed in this exact order:

```text
1. feature/whois-dns
2. feature/subdomain
3. feature/port-scanner
4. feature/banner-tech
5. feature/reporting
6. feature/cli-logging
```

## Critical Rule

**DO NOT move to the next module unless I explicitly tell you to.**

For example:

After completing:

```text
feature/whois-dns
```

STOP.

Do not start:

```text
feature/subdomain
```

until I explicitly say something such as:

```text
Start module 2.
```

This rule applies to every module.

---

# 5. Development Cycle

Every module must follow the same development cycle.

```text
Create / switch to feature branch
        ↓
Inspect existing project
        ↓
Implement ONLY current module
        ↓
Test current module
        ↓
Fix discovered problems
        ↓
Update README.md
        ↓
Review changed files
        ↓
Provide short completion summary
        ↓
Provide recommended git commit
        ↓
STOP
        ↓
Wait for my instruction
```

Do NOT automatically continue to another module.

---

# 6. Git Workflow

For each module:

### Step 1 — Start from the latest main

```bash
git checkout main
git pull origin main
```

### Step 2 — Create the feature branch

Example:

```bash
git checkout -b feature/whois-dns
```

### Step 3 — Develop

Implement ONLY the functionality belonging to that branch.

### Step 4 — Test

Test the functionality and fix problems before considering the module complete.

### Step 5 — Update README

Update `README.md` to reflect the functionality that actually exists.

### Step 6 — Review

Review:

* code
* dependencies
* file structure
* README
* tests
* error handling

### Step 7 — Commit

Create a meaningful commit.

Example:

```bash
git add .
git commit -m "feat: add WHOIS and DNS reconnaissance module"
```

### Step 8 — Push

```bash
git push -u origin feature/whois-dns
```

### Step 9 — STOP

Do not create or start the next branch until I tell you to.

---

# 7. README.md — Permanent Rule

`README.md` is a **living document**.

Do NOT wait until the project is finished to update it.

Update `README.md` whenever meaningful functionality is completed.

This includes:

* New modules
* New CLI features
* New dependencies
* Installation changes
* Usage changes
* Project structure changes
* Testing instructions
* Requirements
* Limitations
* New features

The README must describe the **current implemented state**.

Do NOT document future functionality as if it already exists.

---

# 8. User-Provided Target Rule

The tool must **never hard-code a target domain**.

Do NOT automatically use:

```text
example.com
```

Do NOT automatically choose another domain.

The user must provide the target.

The final CLI should support an interactive workflow such as:

```text
========================================
       CUSTOM RECON TOOL
========================================

Enter domain: example.com
```

The entered domain becomes the target for reconnaissance.

The user could enter:

```text
example.com
example.org
my-authorized-domain.com
```

The tool must work with whichever valid authorized target the user provides.

---

# 9. CLI Target Input

The final application should support:

```bash
python main.py
```

and then ask:

```text
Enter domain:
```

It should also support command-line arguments where appropriate, for example:

```bash
python main.py --domain example.com --dns
```

or:

```bash
python main.py --domain example.com --all
```

If no domain argument is supplied, the application should ask the user interactively.

---

# 10. Module 1 — WHOIS + DNS Enumeration

## Branch

```text
feature/whois-dns
```

## Purpose

Passive reconnaissance.

## Implement

* WHOIS lookup
* DNS A records
* DNS MX records
* DNS TXT records
* DNS NS records
* IP resolution

## File

```text
recon/whois_dns.py
```

Possible functions:

```python
whois_lookup(domain)
dns_lookup(domain)
resolve_domain(domain)
```

Handle:

* Invalid domains
* DNS failures
* Network errors
* Missing records
* WHOIS failures

The module must accept the user-provided domain.

Do not hard-code a domain.

## Completion

After implementation:

1. Test the module.
2. Fix issues.
3. Update `README.md`.
4. Review files.
5. Provide completion summary.
6. Provide recommended commit.
7. STOP.

Do not begin Module 2.

---

# 11. Module 2 — Subdomain Enumeration

## Branch

```text
feature/subdomain
```

## Purpose

Passive subdomain discovery.

## Implement

Use external sources/APIs such as:

```text
crt.sh
```

Optional:

```text
AlienVault OTX
```

## File

```text
recon/subdomains.py
```

Possible function:

```python
enumerate_subdomains(domain)
```

The module should:

* Accept the user-provided domain
* Query the external source
* Extract subdomains
* Normalize results
* Remove duplicates
* Handle API errors
* Handle timeouts
* Handle empty results
* Handle invalid responses

Do not hard-code a target.

## Completion Cycle

Follow the standard development cycle:

```text
Develop
→ Test
→ Fix
→ README update
→ Review
→ Summary
→ Commit recommendation
→ STOP
```

Do not begin Module 3 until instructed.

---

# 12. Module 3 — Port Scanner

## Branch

```text
feature/port-scanner
```

## Purpose

Active reconnaissance.

## Implement

TCP port scanning using:

```text
Nmap wrapper
```

or an appropriate Python socket implementation.

The module should support:

* Target hostname/IP
* Common ports
* Custom ports/ranges where appropriate
* Timeout handling
* Open ports
* Service information where available

Recommended common ports:

```text
21
22
23
25
53
80
110
139
143
443
445
3389
8080
8443
```

Do not perform unnecessarily broad scans by default.

The target must always come from user input.

## Safety

Do not implement:

* Exploitation
* Credential attacks
* Stealth/evasion
* Destructive scanning
* Denial of service

Only implement reconnaissance.

## Completion Cycle

```text
Develop
→ Test
→ Fix
→ README update
→ Review
→ Summary
→ Commit recommendation
→ STOP
```

Do not begin Module 4 until instructed.

---

# 13. Module 4 — Banner Grabbing + Technology Detection

## Branch

```text
feature/banner-tech
```

## Purpose

Identify services and basic web technologies.

## File

```text
recon/banner_tech.py
```

### Banner Grabbing

Possible function:

```python
grab_banner(host, port)
```

Handle:

* Timeouts
* Connection refused
* Empty banners
* Unsupported services

### Technology Detection

Possible function:

```python
detect_technologies(url)
```

Possible detection methods:

* HTTP headers
* Server header
* X-Powered-By
* HTML metadata
* Lightweight fingerprinting

Do not make the project depend on expensive paid services.

The target must come from user input.

## Completion Cycle

```text
Develop
→ Test
→ Fix
→ README update
→ Review
→ Summary
→ Commit recommendation
→ STOP
```

Do not begin Module 5 until instructed.

---

# 14. Module 5 — Reporting

## Branch

```text
feature/reporting
```

## Purpose

Generate reconnaissance reports.

## File

```text
recon/reporting.py
```

Support:

```text
.txt
```

Optional:

```text
.html
```

The report should include:

```text
========================================
RECONNAISSANCE REPORT
========================================

Target:
Timestamp:

IP Resolution:
    IPv4:
    IPv6:

WHOIS:
    ...

DNS:
    A:
    MX:
    TXT:
    NS:

Subdomains:
    ...

Open Ports:
    ...

Service Banners:
    ...

Detected Technologies:
    ...

========================================
END OF REPORT
========================================
```

Use structured data between modules.

Example:

```python
results = {
    "target": "...",
    "timestamp": "...",
    "ip_resolution": {},
    "whois": {},
    "dns": {},
    "subdomains": [],
    "ports": [],
    "banners": {},
    "technologies": []
}
```

The report must display the actual target entered by the user.

Do not hard-code a target.

## Completion Cycle

```text
Develop
→ Test
→ Fix
→ README update
→ Review
→ Summary
→ Commit recommendation
→ STOP
```

Do not begin Module 6 until instructed.

---

# 15. Module 6 — CLI + Logging + Final Integration

## Branch

```text
feature/cli-logging
```

## Purpose

Create the final CLI and logging architecture.

## Files

```text
main.py
recon/logger.py
```

Use Python's:

```python
argparse
```

and:

```python
logging
```

## CLI

The tool should support interactive usage:

```text
========================================
       CUSTOM RECON TOOL
========================================

Enter domain: <USER INPUT>
```

Then allow module selection.

For example:

```text
[1] WHOIS
[2] DNS
[3] Subdomains
[4] Port Scan
[5] Banner Grab
[6] Technology Detection
[7] Run All
[0] Exit

Enter choice:
```

The interface can be improved, but it must remain simple and usable.

## CLI Flags

Support individual module execution such as:

```bash
python main.py --domain example.com --whois
python main.py --domain example.com --dns
python main.py --domain example.com --subdomains
python main.py --domain example.com --ports
python main.py --domain example.com --banner
python main.py --domain example.com --tech
```

Multiple modules:

```bash
python main.py --domain example.com --dns --subdomains --ports
```

All modules:

```bash
python main.py --domain example.com --all
```

Report:

```bash
python main.py --domain example.com --all --report report.txt
```

The exact CLI design can be improved during development.

## Logging

Support appropriate verbosity levels such as:

```text
Normal
Verbose
Debug
```

Example:

```bash
python main.py --domain example.com --all --verbose
```

Do not require a domain to be hard-coded.

---

# 16. Final Integration Cycle

Only after ALL SIX feature branches have been individually completed and approved by me should they be merged into `main`.

The final cycle is:

```text
Module 1 completed
        ↓
Module 2 completed
        ↓
Module 3 completed
        ↓
Module 4 completed
        ↓
Module 5 completed
        ↓
Module 6 completed
        ↓
Review all branches
        ↓
Merge branches into main
        ↓
Resolve conflicts
        ↓
Run complete integration test
        ↓
Update README with final project state
        ↓
Final commit
```

Do not merge branches automatically during individual module development.

---

# 17. Final Project Architecture

The final project should be approximately:

```text
recon-tool/
│
├── main.py
├── plan.md
├── README.md
├── requirements.txt
├── .gitignore
│
├── recon/
│   ├── __init__.py
│   ├── whois_dns.py
│   ├── subdomains.py
│   ├── port_scanner.py
│   ├── banner_tech.py
│   ├── reporting.py
│   ├── logger.py
│   └── utils.py
│
├── reports/
│
└── tests/
    ├── test_whois_dns.py
    ├── test_subdomains.py
    ├── test_port_scanner.py
    ├── test_banner_tech.py
    └── test_reporting.py
```

The exact structure may be adjusted if there is a good technical reason.

Keep modules independent.

---

# 18. Dependencies

Keep dependencies minimal.

Possible dependencies include:

```text
requests
dnspython
python-whois
```

Only add packages that are actually required.

Keep `requirements.txt` updated whenever dependencies change.

---

# 19. Error Handling

One module failing must not unnecessarily crash the entire application.

For example:

```text
[+] WHOIS completed
[+] DNS enumeration completed
[-] Subdomain API unavailable
[+] Port scan completed
[+] Report generated
```

Errors should be clear and useful.

---

# 20. Testing Rules

Testing must use a domain supplied by the user.

Never automatically test against:

```text
example.com
```

Never invent a test domain.

When a real network test is required and no target has been provided, tell me that a target domain is needed.

The agent must not assume permission to scan arbitrary external systems.

Use only domains/systems that I explicitly provide or that are clearly authorized testing targets.

---

# 21. Completion Summary

At the end of EVERY module, provide this exact structure:

## Module Completed

`<branch name>`

## What It Does

2–4 short sentences.

## Files Changed

List created/modified files.

## Functionality Added

Brief list.

## Testing

Briefly state what was tested and the result.

If I did not provide a target domain:

```text
No target domain was provided. The module is ready for testing with a user-supplied authorized target.
```

Do not choose one yourself.

## README Updated

Briefly describe the README changes.

## Dependencies

List dependencies added or changed.

## Recommended Commit

Provide the recommended commit message.

Example:

```text
feat: add WHOIS and DNS reconnaissance module
```

## Next Module

Always state:

> Waiting for my instruction. I will NOT start the next module until I explicitly tell you to.

Then STOP.

---

# 22. Definition of Done

The project is complete only when:

* [ ] All 6 branches are implemented.
* [ ] Each branch has been tested.
* [ ] Each module is independent.
* [ ] README.md has been continuously updated.
* [ ] requirements.txt is accurate.
* [ ] WHOIS works.
* [ ] DNS A/MX/TXT/NS works.
* [ ] IP resolution works.
* [ ] Subdomain enumeration works.
* [ ] Port scanning works.
* [ ] Banner grabbing works.
* [ ] Technology detection works.
* [ ] TXT reporting works.
* [ ] HTML reporting works if implemented.
* [ ] Interactive domain input works.
* [ ] CLI flags work.
* [ ] Logging/verbosity works.
* [ ] Errors are handled gracefully.
* [ ] All branches are merged into `main`.
* [ ] Final integration testing succeeds.
* [ ] Final README accurately describes the completed tool.

---

# 23. CURRENT INSTRUCTION

Start **ONLY** with:

```text
feature/whois-dns
```

Implement only the WHOIS + DNS module.

Do not implement the subdomain module, port scanner, banner/technology module, reporting module, or final CLI yet.

Do not move to the next module until I explicitly tell you.

Follow the complete development cycle:

```text
Branch
→ Inspect
→ Implement
→ Test
→ Fix
→ Update README
→ Review
→ Summary
→ Commit recommendation
→ STOP
```

Wait for my instruction after completion.
