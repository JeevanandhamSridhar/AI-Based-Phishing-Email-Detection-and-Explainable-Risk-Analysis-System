"""Dataset Generation & Preprocessing Script

Creates structured training/testing datasets of legitimate and phishing emails,
and writes synthetic demonstration .eml files clearly marked for educational use.
"""

import json
from pathlib import Path
import random

# Fixed random seed for deterministic dataset generation
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SAMPLES_DIR = BASE_DIR / "data" / "sample_emails"

# -------------------------------------------------------------
# Demonstration Synthetic Emails (.eml fixtures)
# -------------------------------------------------------------
SYNTHETIC_DEMO_EMAILS = [
    {
        "filename": "sample_01_urgent_paypal_phishing.eml",
        "content": (
            "From: PayPal Account Security <security@paypa1-update.com>\n"
            "To: victim@example.com\n"
            "Subject: URGENT: Your PayPal Account Has Been Suspended\n"
            "Date: Sat, 26 Sep 2026 14:20:00 +0000\n"
            "Message-ID: <pp-alert-89342@paypa1-update.com>\n"
            "Reply-To: harvest-inbox@mail-collector.ru\n"
            "Return-Path: <bounce@unverified-mailserver.com>\n"
            "Authentication-Results: mx.google.com; spf=fail; dkim=none; dmarc=fail\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Dear Customer,\n\n"
            "We detected unauthorized access attempts on your PayPal account from an unrecognized IP.\n"
            "To protect your balance, your account has been temporarily restricted.\n\n"
            "Immediate action required within 24 hours to prevent permanent account suspension.\n"
            "Please click the link below to confirm your identity and verify your credentials:\n\n"
            "http://paypal.com.account-update.xyz/verify-login?token=928374\n\n"
            "Failure to act now will result in permanent closure of your account and forfeiture of funds.\n\n"
            "PayPal Security Operations Team\n"
        ),
    },
    {
        "filename": "sample_02_invoice_malware_phishing.eml",
        "content": (
            "From: Accounts Receivable <billing@global-logistics-corp.com>\n"
            "To: accounts@target-company.com\n"
            "Subject: Overdue Payment Notice - Invoice #INV-2026-991\n"
            "Date: Sat, 26 Sep 2026 11:15:00 +0000\n"
            "Message-ID: <inv-notice-552@global-logistics-corp.com>\n"
            "Authentication-Results: spf=softfail; dkim=none\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: multipart/mixed; boundary=\"BOUNDARY_ATTACH_DEMO\"\n"
            "\n"
            "--BOUNDARY_ATTACH_DEMO\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Attention Accounts Payable,\n\n"
            "Your payment for Invoice #INV-2026-991 is now 30 days past due.\n"
            "Failure to settle within 48 hours will trigger immediate legal action and credit reporting.\n"
            "Please review the detailed statement in the attached document.\n\n"
            "Sincerely,\nBilling Department\n"
            "--BOUNDARY_ATTACH_DEMO\n"
            "Content-Type: application/x-msdownload; name=\"Invoice_Statement_Sep2026.pdf.exe\"\n"
            "Content-Disposition: attachment; filename=\"Invoice_Statement_Sep2026.pdf.exe\"\n"
            "Content-Transfer-Encoding: base64\n"
            "\n"
            "TVpQAAIAAAAA//8AALUiAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n"
            "AAAAAABQYXlsb2FkIERlbW8gU3ludGhldGljIEJpbmFyeSBTdHVifj09\n"
            "--BOUNDARY_ATTACH_DEMO--\n"
        ),
    },
    {
        "filename": "sample_03_legitimate_internal_memo.eml",
        "content": (
            "From: HR Department <hr@acme-corp.com>\n"
            "To: all-employees@acme-corp.com\n"
            "Subject: Open Enrollment for 2027 Benefits - Information Session\n"
            "Date: Sat, 26 Sep 2026 09:00:00 +0000\n"
            "Message-ID: <benefits-2027@acme-corp.com>\n"
            "Authentication-Results: mx.google.com; spf=pass; dkim=pass header.i=@acme-corp.com; dmarc=pass\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Dear Acme Corp Team,\n\n"
            "Our annual benefits open enrollment period begins next Monday, October 5th.\n"
            "We have scheduled three optional informational webinars to answer questions regarding\n"
            "health plans, retirement matching, and wellness initiatives.\n\n"
            "You can review the updated benefits handbook on the intranet:\n"
            "https://intranet.acme-corp.com/hr/benefits-2027\n\n"
            "No immediate action is needed today. Please reach out if you have any questions.\n\n"
            "Warm regards,\nAcme Corp Human Resources\n"
        ),
    },
    {
        "filename": "sample_04_legitimate_tech_newsletter.eml",
        "content": (
            "From: Cloud Computing Weekly <editor@cloudweeklynews.org>\n"
            "To: subscriber@target-domain.com\n"
            "Subject: Cloud Architecture Digest #142: Modern Microservices\n"
            "Date: Sat, 26 Sep 2026 08:30:00 +0000\n"
            "Message-ID: <digest-142@cloudweeklynews.org>\n"
            "Authentication-Results: spf=pass; dkim=pass header.i=@cloudweeklynews.org; dmarc=pass\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Welcome to Issue #142 of Cloud Computing Weekly.\n\n"
            "In this edition, we explore container orchestration patterns, eBPF telemetry,\n"
            "and database sharding best practices for distributed systems.\n\n"
            "Read the full articles at our publication portal:\n"
            "https://cloudweeklynews.org/issues/142-microservices\n\n"
            "You received this because you subscribed to our developer newsletter.\n"
            "Manage your preferences or unsubscribe anytime at https://cloudweeklynews.org/unsubscribe\n"
        ),
    },
    {
        "filename": "sample_05_ceo_fraud_wire_transfer.eml",
        "content": (
            "From: Robert Vance <ceo@vance-refrigeration-holding.com>\n"
            "To: finance-lead@target.com\n"
            "Subject: Confidential Acquisition Wire - Urgent Request\n"
            "Date: Sat, 26 Sep 2026 15:45:00 +0000\n"
            "Reply-To: executive-wire-desk@mail-forwarder.xyz\n"
            "Authentication-Results: spf=neutral; dkim=none\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Hi,\n\n"
            "I am currently in an all-day confidential acquisition meeting with our board.\n"
            "We have a closing payment that must be processed immediately before 4 PM today.\n"
            "Please confirm if you are at your desk so I can send the wiring instructions.\n\n"
            "Do not discuss this via phone as the deal is under strict non-disclosure.\n"
            "Reply directly to this email.\n\n"
            "Thanks,\nRobert Vance, CEO\n"
        ),
    },
    {
        "filename": "sample_06_account_security_alert_phishing.eml",
        "content": (
            "From: Microsoft 365 Security <admin@micros0ft-support-alert.com>\n"
            "To: employee@company.com\n"
            "Subject: Action Required: Your Office 365 Password Expires Today\n"
            "Date: Sat, 26 Sep 2026 16:00:00 +0000\n"
            "Authentication-Results: spf=fail; dkim=fail; dmarc=fail\n"
            "X-Project-Origin: Synthetic-Educational-Sample\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n"
            "\n"
            "Your corporate Microsoft 365 access credentials will expire within 12 hours.\n"
            "To prevent interruption to your email and cloud files, keep your current password\n"
            "by authenticating through the single-sign-on verification server:\n\n"
            "http://192.168.1.185/office365/keep-password.php\n\n"
            "Unverified sessions will be disconnected at midnight.\n\n"
            "Microsoft Security Directorate\n"
        ),
    },
]


def generate_demonstration_emails() -> None:
    """Writes the curated synthetic demonstration emails to data/sample_emails/."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    for sample in SYNTHETIC_DEMO_EMAILS:
        path = SAMPLES_DIR / sample["filename"]
        path.write_text(sample["content"], encoding="utf-8")
    print(f"Generated {len(SYNTHETIC_DEMO_EMAILS)} demonstration samples in {SAMPLES_DIR}")


# -------------------------------------------------------------
# Curated Training Corpus (Legitimate + Phishing)
# -------------------------------------------------------------
PHISHING_TEMPLATES = [
    "Urgent: Your {brand} account has been suspended due to unauthorized activity. Verify your identity within 24 hours at {url} to restore full access immediately.",
    "Immediate action required! Your {service} subscription billing failed. Update your payment credentials at {url} to prevent cancellation.",
    "Security Alert: Suspicious login attempt detected from an unknown device. Click here {url} to confirm your password and secure your profile.",
    "Final Warning: Your email storage is 99% full. Your inbox will be blocked unless you validate your credentials here: {url}",
    "Tax refund notification: You are eligible for an unclaimed tax payout of $2,450. Submit your banking details at {url} within 48 hours.",
    "Payroll Department: Mandatory direct deposit update required for next pay cycle. Login to the HR employee portal at {url} immediately.",
    "IT Helpdesk: System maintenance protocol requires all staff to re-authenticate credentials at {url} before end of day.",
    "Package delivery failed: We could not deliver your shipment #US-88492. Pay the $2.99 redelivery fee at {url} to avoid return to sender.",
    "Your {brand} credit line has been locked. Confirm your identity and security PIN at {url} to unlock your card.",
    "Wire transfer authorization required: An outbound payment of $4,800 is pending. If you did not authorize this, cancel immediately at {url}",
]

LEGITIMATE_TEMPLATES = [
    "Hi Team, attached is the revised agenda for our quarterly roadmap meeting this Thursday. Please review slides beforehand at {url}.",
    "Thank you for your order! Your package has shipped and is on schedule for delivery this Friday. Track your shipment at {url}.",
    "Weekly sprint retrospectives are scheduled for 3 PM tomorrow in Conference Room B. Please add your discussion topics to the board: {url}.",
    "Reminder: Open enrollment for next year's health and dental benefits concludes this Friday. Access the employee self-service portal at {url}.",
    "Monthly invoice for your cloud infrastructure subscription is now ready. View and download your receipt in the billing console: {url}.",
    "The engineering design document for the caching service has been published. Please submit your architecture feedback on GitHub: {url}.",
    "Quarterly corporate all-hands meeting will be broadcast live tomorrow at 10 AM. Join the live stream via our internal portal: {url}.",
    "Your weekly performance analytics digest is ready. Review your system uptime and latency metrics on the Grafana dashboard: {url}.",
    "Coffee chat session with new engineering team members this Friday at 11 AM. Looking forward to seeing everyone there.",
    "Maintenance notification: Internal VPN servers will undergo standard security patching on Sunday at 2 AM. Downtime expected under 10 minutes.",
]

BRANDS = ["PayPal", "Microsoft", "Apple", "Google", "Amazon", "Netflix", "Chase", "Wells Fargo", "DocuSign", "Meta"]
SERVICES = ["Office 365", "iCloud", "Amazon Prime", "Netflix Premium", "Google Workspace", "Adobe Creative Cloud"]
PHISHING_URLS = [
    "http://192.168.1.100/login",
    "http://paypal.com.verify-billing.xyz/auth",
    "http://microsoft.com.account-update.top/sso",
    "http://appleid.apple.com.ssl-verify.work/signin",
    "http://secure-banking-portal.buzz/confirm",
    "http://xn--pypal-4ve.com/restore",
    "http://docu-sign.secure-viewer.rest/document",
    "http://netflix.account-validation.country/billing",
]
LEGITIMATE_URLS = [
    "https://intranet.company.com/portal",
    "https://github.com/company/project",
    "https://aws.amazon.com/console",
    "https://portal.office.com/home",
    "https://cloud.google.com/dashboard",
    "https://meet.google.com/abc-defg-hij",
    "https://jira.internal.net/browse/PROJ-102",
]


def build_synthetic_training_dataset(total_samples: int = 600) -> list[dict]:
    """Generates a balanced, randomized dataset of realistic phishing and legitimate emails."""
    dataset = []
    half = total_samples // 2

    # Phishing samples (Label 1)
    for i in range(half):
        tmpl = random.choice(PHISHING_TEMPLATES)
        text = tmpl.format(
            brand=random.choice(BRANDS),
            service=random.choice(SERVICES),
            url=random.choice(PHISHING_URLS),
        )
        dataset.append({
            "id": f"phish_{i:04d}",
            "text": text,
            "label": 1,
            "class_name": "phishing",
        })

    # Legitimate samples (Label 0)
    for i in range(half):
        tmpl = random.choice(LEGITIMATE_TEMPLATES)
        text = tmpl.format(
            url=random.choice(LEGITIMATE_URLS),
        )
        dataset.append({
            "id": f"legit_{i:04d}",
            "text": text,
            "label": 0,
            "class_name": "legitimate",
        })

    random.shuffle(dataset)
    return dataset


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    generate_demonstration_emails()

    print("Building balanced training & validation corpus...")
    dataset = build_synthetic_training_dataset(total_samples=800)
    dataset_path = PROCESSED_DIR / "emails_dataset.json"
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Successfully saved {len(dataset)} balanced email records to {dataset_path}")


if __name__ == "__main__":
    main()
