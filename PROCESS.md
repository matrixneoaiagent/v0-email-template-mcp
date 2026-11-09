# Process

Built on 2026-11-09 by the OpenCode Audit Agent.

1. **Prompt.** A v0-style prompt: a dark, mint-accented product launch email for
   SpendWarden, one clear headline, four feature cards, a code/policy panel, one
   primary CTA, and a short footer. The goal was an email a developer would
   actually read, not a generic newsletter.
2. **Template.** Generated as a single HTML file with inline CSS and a table
   layout for email clients, then hand-tuned: 600px wrapper, mobile media query,
   plain-text fallback, no external images/fonts, accessible contrast.
3. **MCP server.** A FastMCP server with `health`, `render_template`, and
   `send_email`. The send tool builds an `EmailMessage`, sets a Message-ID, and
   tries SMTP; if SMTP is unreachable it writes the RFC822 message and an HTML
   preview into `outbox/` and reports `mode: dry-run` plus the SMTP error.
4. **Test.** `client_demo.py` connects over stdio, lists the tools, calls
   `send_email`, and prints the result. The run produced a real `.eml` and
   preview. OnionMail SMTP timed out from this network; the server did not claim
   a send it could not make.
5. **Evidence.** `preview.png` is the rendered template; `outbox/` holds the
   RFC822 message and HTML preview; this repository is the source.

Limitations: the demo send is a dry-run because the OnionMail SMTP endpoint did
not answer. The server supports a real SMTP send with `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASS`; that path is implemented but not exercised here.
