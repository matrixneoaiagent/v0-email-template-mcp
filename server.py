#!/usr/bin/env python3
"""SpendWarden email MCP server.

A small FastMCP server that renders a responsive email template and sends it
through SMTP.  It is intentionally standard-library only apart from FastMCP:
no wallet keys, no signing, no payment calls, no telemetry.

Run:
    python server.py                 # streamable HTTP on 0.0.0.0:8899
    python server.py --stdio         # stdio MCP transport

SMTP is configured with SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.  If those
are not set, the server falls back to a local dry-run outbox so the MCP flow can
be demonstrated without sending mail.
"""
from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "template.html"
TEXT_TEMPLATE = ROOT / "template.txt"
OUTBOX = ROOT / "outbox"
OUTBOX.mkdir(exist_ok=True)

ACCOUNT = Path("/home/kozak/AI/crypto-wallet/onionmail_account.json")

mcp = FastMCP(
    "SpendWarden Email",
    instructions=(
        "Render a responsive email template and send it through SMTP. "
        "send_email is the only action tool; it never signs or moves money."
    ),
)


def _account() -> dict:
    data: dict = {}
    if ACCOUNT.exists():
        try:
            data = json.loads(ACCOUNT.read_text())
        except Exception:
            data = {}
    return data


def _smtp_config() -> dict:
    acct = _account()
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.onionmail.org"),
        "port": int(os.environ.get("SMTP_PORT", "465")),
        "user": os.environ.get("SMTP_USER", acct.get("email", "")),
        "password": os.environ.get("SMTP_PASS", acct.get("password", "")),
        "from": os.environ.get("SMTP_FROM", acct.get("email", "")),
    }


def _render() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _render_text() -> str:
    if TEXT_TEMPLATE.exists():
        return TEXT_TEMPLATE.read_text(encoding="utf-8")
    return "SpendWarden — your agent can buy things. It can't surprise you."


@mcp.tool
def health() -> dict:
    """Return the server status and which transport mode is configured."""
    cfg = _smtp_config()
    return {
        "ok": True,
        "server": "spendwarden-email-mcp",
        "smtp_configured": bool(cfg["host"] and cfg["user"] and cfg["password"]),
        "smtp_host": cfg["host"],
        "smtp_port": cfg["port"],
        "template": str(TEMPLATE),
        "outbox": str(OUTBOX),
    }


@mcp.tool
def render_template() -> dict:
    """Return the responsive HTML email template and its plain-text fallback."""
    return {
        "ok": True,
        "subject": "SpendWarden — your agent can buy things. It can't surprise you.",
        "html": _render(),
        "text": _render_text(),
    }


@mcp.tool
def send_email(to: str, subject: str, html: str = "", text: str = "") -> dict:
    """Send an HTML email. Falls back to a local dry-run outbox if SMTP is unavailable.

    Args:
        to: recipient address
        subject: email subject
        html: HTML body; empty means use the bundled template
        text: plain-text fallback; empty means use the bundled text template
    """
    body_html = html or _render()
    body_text = text or _render_text()
    cfg = _smtp_config()
    msg = EmailMessage()
    msg["From"] = cfg["from"] or "spendwarden@example.invalid"
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=False)
    msg["Message-ID"] = make_msgid(domain="spendwarden.local")
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")

    result = {
        "ok": True,
        "to": to,
        "subject": subject,
        "from": msg["From"],
        "message_id": msg["Message-ID"],
        "mode": "dry-run",
    }

    if cfg["host"] and cfg["user"] and cfg["password"]:
        try:
            context = ssl.create_default_context()
            if cfg["port"] == 465:
                with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=20) as smtp:
                    smtp.login(cfg["user"], cfg["password"])
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=context)
                    smtp.login(cfg["user"], cfg["password"])
                    smtp.send_message(msg)
            result.update({"mode": "smtp", "smtp_host": cfg["host"], "smtp_port": cfg["port"]})
            return result
        except Exception as exc:  # fall through to the dry-run outbox, with the reason
            result["smtp_error"] = str(exc)[:300]

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    eml = OUTBOX / f"{stamp}-{msg['Message-ID'].split('@')[0].strip('<>')}.eml"
    preview = OUTBOX / f"{stamp}-{msg['Message-ID'].split('@')[0].strip('<>')}.html"
    eml.write_bytes(bytes(msg))
    preview.write_text(body_html, encoding="utf-8")
    result.update({"eml": str(eml), "preview": str(preview)})
    return result


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", "8899")))
    else:
        mcp.run(transport="stdio")
