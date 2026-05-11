# Security Policy

## Supported Versions

We actively support security updates for the following versions of `inundation`:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

As this project is in early development, we recommend always using the latest stable release.

## Reporting a Vulnerability

We take the security of `inundation` seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please use one of the following methods:

#### Preferred: GitHub Security Advisory

1. Go to the [Security tab](https://github.com/ferg-dwr/inundation/security) of the repository
2. Click "Report a vulnerability"
3. Fill out the form with details about the vulnerability

This creates a private security advisory visible only to project maintainers.

#### Alternative: Email

If you cannot use GitHub Security Advisories, you may email:

**fernando.romerogalvan@gmail.com**

Please include the subject line: `[SECURITY] inundation - <brief description>`

### What to Include in Your Report

To help us understand and address the issue quickly, please include:

- **Type of issue** (e.g., data integrity, authentication bypass, injection, etc.)
- **Affected versions** of the package
- **Steps to reproduce** the vulnerability
- **Potential impact** of the vulnerability
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up questions

### What to Expect

After you submit a report, we commit to:

1. **Acknowledge receipt** within 7 days
2. **Provide a detailed response** within 30 days indicating:
   - Confirmation of the vulnerability (or explanation of why it isn't one)
   - Our assessment of severity
   - Our planned timeline for a fix
3. **Notify you** when the vulnerability is patched
4. **Credit you** in the security advisory (unless you prefer to remain anonymous)

### Coordinated Disclosure

We follow a coordinated disclosure process:

1. **Private discussion** with the reporter to understand the issue
2. **Fix development** in a private branch or fork
3. **Patch release** with the security fix
4. **Public disclosure** via GitHub Security Advisory after users have time to update

We typically aim for **90 days** from initial report to public disclosure, though this may vary based on:

- Severity of the vulnerability
- Complexity of the fix
- Reporter's preferences

## Security Considerations for Users

### Data Source Trust

`inundation` downloads data from public government APIs:

- **CDEC** (California Department of Water Resources): `cdec.water.ca.gov`
- **CNRA** (California Natural Resources Agency): `data.cnra.ca.gov`

These are trusted public data sources. However, users should be aware that:

- Data is fetched over HTTPS where supported
- Responses are parsed as CSV/JSON
- Network failures or malicious intermediaries could affect data integrity

### Cache Security

The package caches data in your user cache directory:

- **Linux/macOS:** `~/.cache/inundation/`
- **Windows:** `%LOCALAPPDATA%\inundation\Cache\`

Cache files are:

- Stored with your user's permissions (not world-readable by default)
- Not encrypted (don't store sensitive data in this cache)
- Cleared with `clear_cache()` or by deleting the directory

### Dependencies

We monitor our dependencies for known vulnerabilities through:

- **Dependabot alerts** on GitHub
- **Periodic security audits** of the dependency tree

Run `pip list --outdated` to check for available updates.

## Out of Scope

The following are generally **not** considered security vulnerabilities:

- Issues in third-party data sources (CDEC, CNRA) — please report those to the data providers
- Issues requiring physical access to the user's machine
- Issues that only affect outdated versions of dependencies
- Theoretical vulnerabilities without a practical attack scenario
- Denial of service through resource exhaustion (e.g., requesting decades of data)

## Past Security Advisories

No security advisories have been published for this project yet.

When security advisories are published, they will be listed at:
https://github.com/ferg-dwr/inundation/security/advisories

## Acknowledgments

We appreciate the security research community's efforts in helping keep `inundation` and its users safe. Researchers who responsibly disclose vulnerabilities will be acknowledged here (with their permission):

- _Your name could be here!_

## Questions

For non-security questions about this policy, please open a [GitHub Discussion](https://github.com/ferg-dwr/inundation/discussions) or regular issue.

For security questions, contact: **fernando.romerogalvan@gmail.com**
