"""
AWS Lambda handler — MSCI Poland Inclusion Report
Generates both PDFs and emails them via SES.

Environment variables (set in Lambda config):
  SENDER_EMAIL      - verified SES sender address
  RECIPIENT_EMAIL   - recipient address
  AWS_REGION        - SES region (default: eu-west-1)
"""

import os
import sys
import json
import base64
import logging
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3

# Make the package importable from /var/task (Lambda root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

log = logging.getLogger()
log.setLevel(logging.INFO)

SENDER    = os.environ.get("SENDER_EMAIL",    "marcin.zieba4@gmail.com")
RECIPIENT = os.environ.get("RECIPIENT_EMAIL", "marcin.zieba@yahoo.com")
REGION    = os.environ.get("SES_REGION",      "eu-west-1")

REPORTS = [
    {
        "module":   "examples.generate_march_2026_pdf",
        "function": "build_pdf",
        "out_path": "/tmp/msci_poland_march_2026_update.pdf",
        "filename": "msci_poland_march_2026_update.pdf",
    },
    {
        "module":   "examples.generate_2026_pdf",
        "function": "build_pdf",
        "out_path": "/tmp/msci_poland_2026_candidates.pdf",
        "filename": "msci_poland_2026_candidates.pdf",
    },
]


def _generate_pdfs() -> list[dict]:
    """Import and run each PDF builder; return list of {filename, path} dicts."""
    import importlib
    results = []
    for r in REPORTS:
        log.info("Generating %s ...", r["filename"])
        mod = importlib.import_module(r["module"])
        fn  = getattr(mod, r["function"])
        path = fn(r["out_path"])
        log.info("Saved %s (%d bytes)", path, os.path.getsize(path))
        results.append({"filename": r["filename"], "path": path})
    return results


def _build_email(pdfs: list[dict]) -> bytes:
    """Assemble a MIME multipart message with all PDFs attached."""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = "MSCI Poland Inclusion Reports — March 2026 Update"
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT

    body = MIMEText(
        "Hi,\n\n"
        "Please find attached the latest MSCI Poland inclusion research reports:\n\n"
        "1. msci_poland_march_2026_update.pdf — March 2026 confirmed changes + May 2026 trade setup\n"
        "2. msci_poland_2026_candidates.pdf   — Full verified candidate list with conviction ratings\n\n"
        "⚠  All [EST] figures require live verification before trading.\n"
        "   PLN/USD rate used: 3.68 (March 6, 2026).\n\n"
        "This email was generated automatically by the MSCI Poland Lambda function.\n",
        "plain",
    )
    msg.attach(body)

    for pdf in pdfs:
        with open(pdf["path"], "rb") as f:
            data = f.read()
        part = MIMEBase("application", "octet-stream")
        part.set_payload(data)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment",
                        filename=pdf["filename"])
        msg.attach(part)

    return msg.as_bytes()


def _send_via_ses(raw_bytes: bytes) -> dict:
    """Send pre-built MIME email through SES."""
    client = boto3.client("ses", region_name=REGION)
    resp = client.send_raw_email(
        Source=SENDER,
        Destinations=[RECIPIENT],
        RawMessage={"Data": raw_bytes},
    )
    log.info("SES MessageId: %s", resp["MessageId"])
    return resp


def _verify_emails() -> dict:
    """
    Trigger SES verification for SENDER and RECIPIENT using the Lambda's IAM role.
    Invoke once with event={"action":"verify"} then click the links in both inboxes.
    """
    client = boto3.client("ses", region_name=REGION)
    results = {}
    for email in [SENDER, RECIPIENT]:
        attrs = client.get_identity_verification_attributes(Identities=[email])
        status = attrs["VerificationAttributes"].get(email, {}).get("VerificationStatus", "")
        if status == "Success":
            results[email] = "already_verified"
        else:
            client.verify_email_identity(EmailAddress=email)
            results[email] = "verification_email_sent"
    log.info("SES verification results: %s", results)
    return results


def handler(event, context):
    """
    Lambda entry point.
    event={}                    → generate PDFs and email them
    event={"action":"verify"}  → send SES verification emails to SENDER and RECIPIENT
    """
    log.info("Event: %s", json.dumps(event))
    action = event.get("action", "report") if isinstance(event, dict) else "report"

    try:
        if action == "verify":
            results = _verify_emails()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "SES verification triggered. Check inboxes and click the AWS links.",
                    "results": results,
                }),
            }

        pdfs     = _generate_pdfs()
        raw      = _build_email(pdfs)
        ses_resp = _send_via_ses(raw)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Reports generated and emailed successfully.",
                "ses_message_id": ses_resp["MessageId"],
                "reports": [p["filename"] for p in pdfs],
            }),
        }
    except Exception as exc:
        log.exception("Lambda failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)}),
        }
