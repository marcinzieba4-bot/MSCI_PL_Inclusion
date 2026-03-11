"""
AWS Lambda handler — MSCI + FTSE Poland Inclusion Report (Combined)
====================================================================
Generates three PDFs (MSCI-only, MSCI candidates watchlist, combined MSCI+FTSE)
and a JSON summary, saves them all to S3 (s3bucketmz/Strategies/), then
emails the PDFs via SES.

Environment variables (set in Lambda config):
  SENDER_EMAIL      - verified SES sender address
  RECIPIENT_EMAIL   - recipient address
  SES_REGION        - SES region (default: eu-north-1)
  S3_BUCKET         - target S3 bucket (default: s3bucketmz)
  S3_PREFIX         - key prefix inside bucket (default: Strategies)
"""

import os
import sys
import json
import logging
from datetime import date
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
REGION    = os.environ.get("SES_REGION",      "eu-north-1")
S3_BUCKET = os.environ.get("S3_BUCKET",       "s3bucketmz")
S3_PREFIX = os.environ.get("S3_PREFIX",       "Strategies")

_TODAY = date.today().strftime("%Y-%m-%d")

REPORTS = [
    {
        "module":   "examples.generate_march_2026_pdf",
        "function": "build_pdf",
        "out_path": "/tmp/msci_poland_march_2026_update.pdf",
        "filename": "msci_poland_march_2026_update.pdf",
        "s3_key":   f"{S3_PREFIX}/msci_poland_march_2026_update_{_TODAY}.pdf",
    },
    {
        "module":   "examples.generate_2026_pdf",
        "function": "build_pdf",
        "out_path": "/tmp/msci_poland_2026_candidates.pdf",
        "filename": "msci_poland_2026_candidates.pdf",
        "s3_key":   f"{S3_PREFIX}/msci_poland_2026_candidates_{_TODAY}.pdf",
    },
    {
        "module":   "examples.generate_combined_pdf",
        "function": "build_pdf",
        "out_path": "/tmp/poland_combined_inclusion_2026.pdf",
        "filename": "poland_combined_inclusion_2026.pdf",
        "s3_key":   f"{S3_PREFIX}/poland_combined_inclusion_2026_{_TODAY}.pdf",
    },
]

_JSON_TMP_PATH = "/tmp/poland_inclusion_2026_summary.json"
_JSON_S3_KEY   = f"{S3_PREFIX}/poland_inclusion_2026_summary_{_TODAY}.json"


# ─────────────────────────────────────────────────────────────────────────────
# PDF generation
# ─────────────────────────────────────────────────────────────────────────────

def _generate_pdfs() -> list[dict]:
    """Import and run each PDF builder; return list of {filename, path, s3_key} dicts."""
    import importlib
    results = []
    for r in REPORTS:
        log.info("Generating %s ...", r["filename"])
        mod = importlib.import_module(r["module"])
        fn  = getattr(mod, r["function"])
        path = fn(r["out_path"])
        log.info("Saved %s (%d bytes)", path, os.path.getsize(path))
        results.append({"filename": r["filename"], "path": path, "s3_key": r["s3_key"]})
    return results


# ─────────────────────────────────────────────────────────────────────────────
# JSON generation
# ─────────────────────────────────────────────────────────────────────────────

def _generate_json() -> dict:
    """Build the combined report data model + backtest and save as JSON to /tmp."""
    from examples.combined_report_2026 import build_combined_report
    from examples.backtest_combined_2026 import build_combined_backtest, to_json_dict as backtest_to_json
    report = build_combined_report()
    data = report.to_json_dict()
    # Attach backtest results
    bt_result = build_combined_backtest()
    data["backtest"] = backtest_to_json(bt_result)
    with open(_JSON_TMP_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    log.info("JSON saved to %s (%d bytes)", _JSON_TMP_PATH, os.path.getsize(_JSON_TMP_PATH))
    return data


# ─────────────────────────────────────────────────────────────────────────────
# S3 upload
# ─────────────────────────────────────────────────────────────────────────────

def _upload_to_s3(local_path: str, s3_key: str, content_type: str) -> str:
    """Upload a local file to S3; return the S3 URI."""
    s3 = boto3.client("s3", region_name=REGION)
    s3.upload_file(
        local_path,
        S3_BUCKET,
        s3_key,
        ExtraArgs={"ContentType": content_type},
    )
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    log.info("Uploaded %s → %s", local_path, s3_uri)
    return s3_uri


def _save_all_to_s3(pdfs: list[dict]) -> dict:
    """Upload all PDFs and the JSON to S3; return map of filename → S3 URI."""
    uploaded = {}
    for pdf in pdfs:
        uri = _upload_to_s3(pdf["path"], pdf["s3_key"], "application/pdf")
        uploaded[pdf["filename"]] = uri
    json_uri = _upload_to_s3(_JSON_TMP_PATH, _JSON_S3_KEY, "application/json")
    uploaded["poland_inclusion_2026_summary.json"] = json_uri
    return uploaded


# ─────────────────────────────────────────────────────────────────────────────
# Email (SES)
# ─────────────────────────────────────────────────────────────────────────────

def _build_email(pdfs: list[dict], json_data: dict, s3_uris: dict) -> bytes:
    """Assemble a MIME multipart message with all PDFs attached."""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = "Poland Index Inclusion Reports 2026 — MSCI + FTSE Combined"
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT

    d = json_data.get("summary", {})
    body_text = (
        "Hi,\n\n"
        "Please find attached the 2026 Poland index inclusion research reports.\n\n"
        "REPORTS ATTACHED:\n"
        "  1. poland_combined_inclusion_2026.pdf\n"
        "     → Combined MSCI + FTSE report with dual-index plays, individual views,\n"
        "       and full trade action list.\n\n"
        "  2. msci_poland_march_2026_update.pdf\n"
        "     → MSCI-only March 2026 update (Feb 2026 SAR outcome + live market data).\n\n"
        "  3. msci_poland_2026_candidates.pdf\n"
        "     → Full MSCI Poland 2026 candidate watchlist with threshold mechanics.\n\n"
        "COMBINED REPORT SUMMARY:\n"
        f"  Total trades:            {d.get('total_trades', '—')}\n"
        f"  Dual-index plays (★):    {d.get('dual_index', '—')}  (MSCI + FTSE same stock)\n"
        f"  MSCI-only trades:        {d.get('msci_only', '—')}\n"
        f"  FTSE-only trades:        {d.get('ftse_only', '—')}\n"
        f"  HIGH conviction:         {d.get('high_conviction', '—')}\n"
        f"  Total forced buying est: ${d.get('total_est_forced_buying_usd_m', 0):.0f}M\n\n"
        "TOP DUAL-INDEX PLAYS:\n"
        "  XTB  — MSCI May 2026 SAR + FTSE Jun 2026 QIR  | Combined FB [EST]: ~$425M\n"
        "  Kruk — MSCI Nov 2026 SAR + FTSE Sep 2026 QIR  | Combined FB [EST]: ~$315M\n\n"
        "S3 FILES SAVED:\n"
    )
    for fname, uri in s3_uris.items():
        body_text += f"  {fname}\n  → {uri}\n"

    body_text += (
        "\n⚠  All [EST] figures require live verification before trading.\n"
        "   PLN/USD rate used: 3.68 (March 6, 2026).\n"
        "   FTSE Poland = Developed Market (since Sep 2018) — NOT Emerging.\n\n"
        "This email was generated automatically by the MSCI+FTSE Poland Lambda function.\n"
    )
    msg.attach(MIMEText(body_text, "plain"))

    for pdf in pdfs:
        with open(pdf["path"], "rb") as f:
            data = f.read()
        part = MIMEBase("application", "octet-stream")
        part.set_payload(data)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=pdf["filename"])
        msg.attach(part)

    # Attach JSON summary
    with open(_JSON_TMP_PATH, "rb") as f:
        json_bytes = f.read()
    json_part = MIMEBase("application", "json")
    json_part.set_payload(json_bytes)
    encoders.encode_base64(json_part)
    json_part.add_header("Content-Disposition", "attachment",
                         filename="poland_inclusion_2026_summary.json")
    msg.attach(json_part)

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


# ─────────────────────────────────────────────────────────────────────────────
# SES email verification helper
# ─────────────────────────────────────────────────────────────────────────────

def _verify_emails() -> dict:
    """
    Trigger SES verification for SENDER and RECIPIENT.
    Invoke with event={"action":"verify"} then click the AWS links in both inboxes.
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


# ─────────────────────────────────────────────────────────────────────────────
# Lambda entry point
# ─────────────────────────────────────────────────────────────────────────────

def handler(event, context):
    """
    Lambda entry point.

    event={}                        → generate PDFs + JSON, save to S3, email them
    event={"action":"verify"}       → send SES verification emails
    event={"action":"s3_only"}      → generate + save to S3, no email
    event={"action":"json_only"}    → generate JSON only, save to S3
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

        if action == "json_only":
            json_data = _generate_json()
            json_uri  = _upload_to_s3(_JSON_TMP_PATH, _JSON_S3_KEY, "application/json")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "JSON generated and saved to S3.",
                    "s3_uri": json_uri,
                    "summary": json_data.get("summary", {}),
                }),
            }

        # Generate all outputs
        pdfs      = _generate_pdfs()
        json_data = _generate_json()

        # Save to S3
        s3_uris = _save_all_to_s3(pdfs)
        log.info("All files saved to S3 bucket '%s' under prefix '%s'", S3_BUCKET, S3_PREFIX)

        if action == "s3_only":
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Reports generated and saved to S3.",
                    "s3_uris": s3_uris,
                    "reports": [p["filename"] for p in pdfs],
                    "summary": json_data.get("summary", {}),
                }),
            }

        # Full flow: generate + S3 + email
        raw      = _build_email(pdfs, json_data, s3_uris)
        ses_resp = _send_via_ses(raw)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Reports generated, saved to S3, and emailed successfully.",
                "ses_message_id": ses_resp["MessageId"],
                "reports": [p["filename"] for p in pdfs],
                "s3_uris": s3_uris,
                "summary": json_data.get("summary", {}),
            }),
        }

    except Exception as exc:
        log.exception("Lambda failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)}),
        }
