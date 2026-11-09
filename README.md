# v0-style email template + MCP send server

A responsive, email-client-safe HTML template for **SpendWarden**, plus a small
[FastMCP](https://gofastmcp.com) server that exposes a `send_email` tool.

The template is a dark, mint-accented product launch email built from a v0-style
prompt and then customized by hand: inline CSS, table layout, 600px wrapper,
mobile media query, plain-text fallback, and no external images or fonts.

## What is here

| File | Purpose |
|---|---|
| `template.html` | responsive HTML email (inline CSS, table layout) |
| `template.txt` | plain-text fallback |
| `server.py` | FastMCP server: `health`, `render_template`, `send_email` |
| `client_demo.py` | calls the server over FastMCP stdio and prints the result |
| `outbox/` | RFC822 `.eml` and HTML preview from the dry-run demo |
| `preview.png` | rendered preview of the template |

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install fastmcp
.venv/bin/python server.py             # streamable HTTP on 0.0.0.0:8899
# or
.venv/bin/python client_demo.py        # stdio MCP client demo
```

The MCP tools are:

- `health()` — server status and SMTP configuration state.
- `render_template()` — returns the HTML and plain-text template.
- `send_email(to, subject, html="", text="")` — sends via SMTP, or writes an
  `.eml` + preview to `outbox/` when SMTP is not configured/reachable.

SMTP is configured with `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`,
`SMTP_FROM`. The server never signs, moves money, or stores wallet keys.

## Demo result

`client_demo.py` listed the three tools and called `send_email`:

```json
{"ok":true,"to":"opencode.agent177c@onionmail.org","subject":"SpendWarden email template demo","mode":"dry-run","smtp_error":"timed out","eml":"outbox/20261109T194259Z-...eml","preview":"outbox/...html"}
```

The OnionMail SMTP host did not answer from this network, so the server wrote a
real RFC822 message to `outbox/` instead of claiming a send. With a reachable
SMTP host and credentials, the same tool sends the message and returns
`"mode":"smtp"`.

## Template preview

Open `template.html` or the rendered `preview.png`. The public source is this
repository; pin the commit for a durable reference.

## License

MIT.
