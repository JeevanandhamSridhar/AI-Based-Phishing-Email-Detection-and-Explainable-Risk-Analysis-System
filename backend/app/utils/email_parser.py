"""Static RFC-822 / MIME Email Parser

Performs safe lexical and structural decomposition of emails without executing attachments
or initiating outbound network requests.
"""

import email
from email import policy
from email.utils import parseaddr
import hashlib
import re
from typing import List, Set, Tuple
from bs4 import BeautifulSoup
from app.schemas.email import ParsedEmail, HeaderInfo, AttachmentMetadata

# Dangerous executable and script file extensions
EXECUTABLE_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".jse", ".wsf", ".wsh",
    ".ps1", ".ps1xml", ".ps2", ".psc1", ".psc2", ".msc", ".jar", ".iso",
    ".img", ".vhd", ".vhdx", ".hta", ".cpl", ".msi", ".msp", ".pif", ".gadget"
}

# Macro-enabled office document extensions
MACRO_EXTENSIONS = {
    ".docm", ".dotm", ".xlsm", ".xltm", ".xlam", ".pptm", ".potm", ".ppam", ".ppsm", ".sldm"
}

# Regex to safely find URLs in plain text without visiting
URL_REGEX = re.compile(
    r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
    re.VERBOSE
)


def extract_domain_from_email(email_str: str) -> str:
    """Extracts the domain portion of an email address."""
    _, addr = parseaddr(email_str)
    if "@" in addr:
        return addr.split("@")[-1].strip().lower()
    return ""


def check_double_extension(filename: str) -> Tuple[bool, str]:
    """Detects deceptive double-extension patterns (e.g. invoice.pdf.exe)."""
    parts = filename.lower().split(".")
    if len(parts) >= 3:
        second_last = "." + parts[-2]
        last = "." + parts[-1]
        common_doc_exts = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".rtf", ".png", ".jpg"}
        if second_last in common_doc_exts and (last in EXECUTABLE_EXTENSIONS or last in MACRO_EXTENSIONS):
            return True, last
    ext = ("." + parts[-1]) if len(parts) > 1 else ""
    return False, ext


def sanitize_text(text: str) -> str:
    """Normalizes whitespace and removes null bytes from text."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    return re.sub(r"[ \t]+", " ", text).strip()


def parse_email(raw_input: str, file_name: str = None) -> ParsedEmail:
    """Safely decomposes a raw email string into structured headers, body, URLs, and attachments."""
    # Compute SHA-256 fingerprint of the complete email content
    raw_bytes = raw_input.encode("utf-8", errors="replace")
    email_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    # Parse using Python email library with standard modern policy
    msg = email.message_from_string(raw_input, policy=policy.default)

    # 1. Extract Headers
    raw_headers = {}
    for key in msg.keys():
        raw_headers[key] = str(msg[key])

    from_header = str(msg.get("From", ""))
    sender_name, sender_email = parseaddr(from_header)
    sender_domain = extract_domain_from_email(sender_email)

    to_header = str(msg.get("To", ""))
    subject = str(msg.get("Subject", "(No Subject)"))
    date = str(msg.get("Date", ""))

    reply_to = msg.get("Reply-To")
    reply_to_str = str(reply_to) if reply_to else None
    reply_to_domain = extract_domain_from_email(reply_to_str) if reply_to_str else None

    return_path = msg.get("Return-Path")
    return_path_str = str(return_path) if return_path else None
    return_path_domain = extract_domain_from_email(return_path_str) if return_path_str else None

    message_id = str(msg.get("Message-ID", "")) or None
    auth_results = str(msg.get("Authentication-Results", "")) or None
    received_spf = str(msg.get("Received-SPF", "")) or None

    header_info = HeaderInfo(
        from_header=from_header,
        sender_name=sender_name,
        sender_email=sender_email,
        sender_domain=sender_domain,
        to_header=to_header,
        subject=subject,
        date=date,
        reply_to=reply_to_str,
        reply_to_domain=reply_to_domain,
        return_path=return_path_str,
        return_path_domain=return_path_domain,
        message_id=message_id,
        authentication_results=auth_results,
        received_spf=received_spf,
        raw_headers=raw_headers,
    )

    # 2. Extract Body and Attachments
    body_plain_parts = []
    body_html_parts = []
    attachments: List[AttachmentMetadata] = []
    extracted_urls: Set[str] = set()

    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get_content_disposition() or "")
        filename = part.get_filename()

        # Check if part is an attachment
        if filename or "attachment" in content_disposition:
            fname = filename or "unnamed_attachment"
            payload_bytes = part.get_payload(decode=True) or b""
            size_bytes = len(payload_bytes)
            attach_sha256 = hashlib.sha256(payload_bytes).hexdigest()

            is_double, detected_ext = check_double_extension(fname)
            if not detected_ext:
                detected_ext = ("." + fname.split(".")[-1].lower()) if "." in fname else ""

            is_exec = detected_ext in EXECUTABLE_EXTENSIONS or is_double
            is_macro = detected_ext in MACRO_EXTENSIONS

            attachments.append(
                AttachmentMetadata(
                    filename=fname,
                    extension=detected_ext,
                    double_extension=is_double,
                    mime_type=content_type,
                    size_bytes=size_bytes,
                    sha256=attach_sha256,
                    is_executable=is_exec,
                    is_macro_enabled=is_macro,
                )
            )
            continue

        # Extract textual content
        if content_type == "text/plain":
            try:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="replace")
                body_plain_parts.append(text)
            except Exception:
                pass
        elif content_type == "text/html":
            try:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                html = payload.decode(charset, errors="replace")
                body_html_parts.append(html)
            except Exception:
                pass

    # Assemble and clean plain text & HTML
    raw_plain = "\n".join(body_plain_parts)
    raw_html = "\n".join(body_html_parts)

    # If no plain text was found in MIME parts, check if raw_input was just text
    if not raw_plain and not raw_html:
        raw_plain = raw_input

    # Parse HTML for links and fallback text
    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")
        # Strip script and style tags to prevent execution or analysis interference
        for element in soup(["script", "style", "noscript"]):
            element.extract()

        # Extract URLs from anchor href attributes
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if href.startswith(("http://", "https://")):
                extracted_urls.add(href)

        # If plain body was empty, use cleaned HTML text
        if not raw_plain.strip():
            raw_plain = soup.get_text(separator=" ")

    # Extract URLs from plain body text via regex
    for match in URL_REGEX.finditer(raw_plain):
        url = match.group(0).strip()
        # Clean trailing punctuation
        url = re.sub(r"[.,;:!]+$", "", url)
        if url.startswith(("http://", "https://", "www.")):
            if url.startswith("www."):
                url = "http://" + url
            extracted_urls.add(url)

    # Clean text
    clean_plain = sanitize_text(raw_plain)
    clean_html = sanitize_text(raw_html)

    return ParsedEmail(
        headers=header_info,
        body_plain=clean_plain,
        body_html=clean_html,
        urls=sorted(list(extracted_urls)),
        attachments=attachments,
        sha256=email_sha256,
    )
