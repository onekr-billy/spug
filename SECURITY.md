# Security Policy

English | [简体中文](SECURITY-zh_CN.md)

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Public reports expose unpatched installations before a fix is available. Spug is a
self-hosted operations platform that holds SSH credentials and can execute commands
on managed hosts, so premature disclosure puts other people's infrastructure at risk.

### Preferred: GitHub Private Vulnerability Reporting

Private vulnerability reporting is enabled on this repository.

1. Go to the [Security Advisories](https://github.com/openspug/spug/security/advisories) page.
2. Click **"Report a vulnerability"**.
3. Fill in the form with the details described in [What to include](#what-to-include).

You will need a GitHub account to submit the report. Reports submitted this way are
visible only to repository maintainers and to you.

### Alternative: Email

If you cannot use GitHub private reporting, email **spug.dev@gmail.com**.

Please use `[SECURITY]` as the subject prefix. If you have a PGP key preference or
want the reply encrypted, say so in the first message and we will arrange it.

### What to include

The more of the following you can provide, the faster we can triage and fix:

- The affected component and file path (e.g. `spug_api/apps/monitor/executors.py`)
- The affected version(s) and/or branch, and the commit hash if you tested against one
- A step-by-step reproduction, including the exact request, payload, or input
- The privileges required to reproduce (unauthenticated / normal user / host-scoped user / admin)
- The observed impact versus the expected behaviour
- Any suggested fix or mitigation you have in mind

A minimal but working proof of concept is far more useful than a long description.
Please keep PoC payloads non-destructive.

## Scope

### In scope

Security defects in Spug itself that let an attacker exceed the privileges the
product is designed to grant, for example:

- Authentication bypass, session or access token weaknesses, MFA/LDAP bypass
- Privilege escalation between accounts or roles
- Broken authorization on host-scoped operations — a user acting on hosts they
  were never granted
- Injection reaching a shell or interpreter through an unintended path
  (command, SQL, template, LDAP filter, deserialization)
- Server-side request forgery, path traversal, arbitrary file read/write outside
  the intended file-manager scope
- Cross-site scripting, CSRF, or clickjacking against the web console
- Secrets exposure: host credentials, private keys, configuration-center values
  leaking through responses, logs, exports, or error messages
- Vulnerabilities in bundled or pinned dependencies that are reachable in Spug

### Out of scope

Spug is an automation and operations platform. Several of its headline features
exist to run commands on remote hosts over SSH. The following are **by design**
and are not vulnerabilities:

- Executing commands, uploading files, or opening a terminal on a host that the
  authenticated user *is* authorized for
- Administrative capabilities available to a superuser account (`is_supper`)
- The custom-script monitor type (type 4) executing its configured command on its
  configured target — that is the documented purpose of the feature
- Anything requiring physical access, an already-compromised admin account, or
  an attacker who already holds valid SSH credentials for a managed host
- Missing rate limiting, user enumeration via timing, or open registration
  without a demonstrated security impact
- Reports from automated scanners that do not demonstrate a concrete impact
- Deployment and hardening guidance (reverse-proxy TLS, OS hardening, database
  exposure). See [docs](https://ops.spug.cc/docs/about-spug/) instead.

If you are unsure whether something qualifies, report it privately anyway — we
would rather assess it than have you guess wrong.

## Supported Versions

| Branch / line | Status | Notes |
| --- | --- | --- |
| `4.0` (default branch) | Supported | Receives security fixes |
| `master` (v2.3.x) | End of life | Last updated 2022. No fixes will be issued |
| Earlier releases | End of life | No fixes will be issued |

Only the default branch receives security patches. If you are running an
end-of-life version, please upgrade — we will not backport fixes to it.

When we publish a fix, the affected versions are recorded in the corresponding
GitHub Security Advisory.

## Our Response Process

| Stage | Target |
| --- | --- |
| Acknowledge receipt | 3 business days |
| Initial triage and severity assessment | 7 business days |
| Status update to reporter | Every 7 business days while open |
| Fix released or mitigation published | Depends on severity; we aim for the next patch release |

These are targets, not guarantees — Spug is maintained by a small team.
If we miss one, reply to the advisory thread and we will get back to you.

Severity is assessed with [CVSS v3.1](https://www.first.org/cvss/calculator/3.1)
in the context of a default Spug deployment.

## Disclosure Timeline

- We ask for **90 days** from acknowledgement before public disclosure, or until a
  fix ships, whichever comes first.
- We will tell you in the advisory thread once a fix is released, so you can
  publish on your side too.
- We will not ask for an indefinite embargo. If we cannot fix within 90 days, we
  will discuss a timeline with you rather than stall.
- If you find the same issue is already being tracked, we will let you know and
  can credit you as an additional finder.

## Credit

Reporters who follow this policy are credited in the published GitHub Security
Advisory, unless you ask to remain anonymous. Thank you for helping keep Spug and
the infrastructure it manages secure.

## Safe Harbour

We consider security research conducted in good faith under this policy to be
authorized. We will not pursue legal action against you, and we will not file a
DMCA or other complaint against your write-up, provided that you:

- Report privately first and avoid public disclosure during the agreed window
- Test only against installations you own or have explicit permission to test
- Do not access, modify, or exfiltrate data belonging to other users
- Do not degrade, disrupt, or destroy systems or services
- Keep any PoC non-destructive and delete data you incidentally obtained

The public demo environment at [demo.spug.cc](https://demo.spug.cc) is available
for evaluation, but it is shared and resets hourly — **do not** use it for
testing that could affect other users, and do not treat it as permission to test
production installations.

This is a statement of our intent, not a binding legal agreement.

## Bug Bounty

Spug does not currently run a paid bug bounty program. Recognition in the
advisory is what we can offer.

## Maintainer Notes

- This policy lives on the **default branch**. GitHub only surfaces the security
  policy link for the repository when the file is present there.
- Keep this file free of vulnerability details. Never document an unfixed issue here.
