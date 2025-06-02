# Security Policy for ShowTrackr

We appreciate your efforts to responsibly disclose any security vulnerabilities you might find in ShowTrackr.

## Reporting a Vulnerability

If you discover a security vulnerability, we encourage you to report it responsibly.

**GitHub Security Advisories**

You can create a new security advisory directly within the ShowTrackr repository. This allows for private discussion and coordinated disclosure if necessary.

1.  Go to the "Security" tab of the ShowTrackr GitHub repository.
2.  Click on "Advisories".
3.  Click "New advisory" to create a private vulnerability report.
    - Direct link (if you have permissions, otherwise the maintainer will use this): `https://github.com/Exonymos/ShowTrackr-Web/security/advisories/new`

**Please include the following details with your report:**

- A clear description of the vulnerability.
- Steps to reproduce the vulnerability, including any specific URLs, configurations, or sequences of actions.
- The potential impact of the vulnerability.
- Any proof-of-concept code, screenshots, or videos that help demonstrate the vulnerability.
- Your name or alias for acknowledgement (if desired).

## Scope

This security policy applies to the latest released version of ShowTrackr and the `main` branch. Vulnerabilities in third-party dependencies should ideally be reported to the respective project maintainers first.

## Important Considerations for a Local Application

ShowTrackr is designed to be run locally on your own computer. As such:

- The primary security focus is on preventing vulnerabilities that could be exploited through web browser interactions if the application is run in an unsafe manner (e.g., exposing it to untrusted networks without proper precautions) or through malicious data import.
- Data is stored locally in a SQLite database file (`data/database.db`) and configuration in `data/.env`. Physical security of your machine and these files is your responsibility.
- Ensure your local Python environment and dependencies are kept up-to-date.

Thank you for helping keep ShowTrackr secure!
