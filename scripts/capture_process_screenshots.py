import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

FRONTEND_URL = "http://127.0.0.1:5174/"

def capture_all_screenshots():
    print("=" * 70)
    print("PHISHGUARD SOC: CAPTURING PROCESS OPERATION SCREENSHOTS")
    print("=" * 70)
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Using Browser:    {CHROME_PATH}")
    print(f"Target URL:       {FRONTEND_URL}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 920},
            device_scale_factor=1.5
        )
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. Workspace Initial State
        # -------------------------------------------------------------
        print("[1/16] Capturing 01_workspace_initial_state.png...")
        page.goto(FRONTEND_URL, wait_until="networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUTPUT_DIR / "01_workspace_initial_state.png"))

        # -------------------------------------------------------------
        # 2. Your Tested & Uploaded Emails Tab
        # -------------------------------------------------------------
        print("[2/16] Capturing 02_user_tested_emails_tab.png...")
        tested_tab_btn = page.locator("button:has-text('Your Tested')")
        if tested_tab_btn.count() > 0:
            tested_tab_btn.first.click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUTPUT_DIR / "02_user_tested_emails_tab.png"))
            # Switch back to presets
            presets_tab_btn = page.locator("button:has-text('Synthetic Presets')")
            if presets_tab_btn.count() > 0:
                presets_tab_btn.first.click()
                page.wait_for_timeout(400)

        # -------------------------------------------------------------
        # 3. Loading Threat Sample Preset (PayPal)
        # -------------------------------------------------------------
        print("[3/16] Capturing 03_loading_threat_sample.png...")
        paypal_card = page.locator("div:has-text('PayPal Account Has Been Suspended')").first
        if paypal_card.count() > 0:
            paypal_card.click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "03_loading_threat_sample.png"))

        # -------------------------------------------------------------
        # 4. Trigger Analysis & Capture Radar Scan HUD
        # -------------------------------------------------------------
        print("[4/16] Capturing 04_triage_radar_scan_progress.png...")
        analyze_btn = page.locator("button:has-text('Execute Risk Analysis')").first
        if analyze_btn.count() > 0:
            analyze_btn.click()
            # Capture radar HUD immediately while loading
            page.wait_for_timeout(350)
            page.screenshot(path=str(OUTPUT_DIR / "04_triage_radar_scan_progress.png"))

        # Wait for ResultView to load completely
        page.wait_for_selector("text=Incident ID", timeout=15000)
        page.wait_for_timeout(1500) # Allow score count-up animation to complete

        # -------------------------------------------------------------
        # 5. Incident Report Overview & Risk Meter
        # -------------------------------------------------------------
        print("[5/16] Capturing 05_incident_report_overview.png...")
        page.screenshot(path=str(OUTPUT_DIR / "05_incident_report_overview.png"))

        # -------------------------------------------------------------
        # 6. Factor Breakdown Math
        # -------------------------------------------------------------
        print("[6/16] Capturing 06_factor_breakdown_math.png...")
        factor_card = page.locator("h3:has-text('Weighted Factor Decomposition'), h3:has-text('Factor Decomposition')").first
        if factor_card.count() > 0:
            factor_card.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "06_factor_breakdown_math.png"))
        else:
            print("Warning: factor_card selector not found, attempting fallback scroll...")
            page.evaluate("window.scrollBy(0, 400)")
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "06_factor_breakdown_math.png"))

        # -------------------------------------------------------------
        # 7. XAI Attribution Waterfall
        # -------------------------------------------------------------
        print("[7/16] Capturing 07_xai_attribution_waterfall.png...")
        xai_card = page.locator("h3:has-text('Explainable AI (XAI) Attribution')").first
        if xai_card.count() > 0:
            xai_card.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "07_xai_attribution_waterfall.png"))

        # -------------------------------------------------------------
        # 8. Forensic Inspector - In-Body XAI Highlighter (Tab 1)
        # -------------------------------------------------------------
        print("[8/16] Capturing 08_forensic_in_body_xai.png...")
        forensic_box = page.locator("button:has-text('Interactive In-Body XAI')").first
        if forensic_box.count() > 0:
            forensic_box.click()
            forensic_box.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            # Hover over a highlighted token to show popover tooltip
            phish_tokens = page.locator(".xai-token-phish, span[class*='border-red-500']")
            if phish_tokens.count() > 0:
                phish_tokens.first.hover()
                page.wait_for_timeout(400)
            page.screenshot(path=str(OUTPUT_DIR / "08_forensic_in_body_xai.png"))

        # -------------------------------------------------------------
        # 9. Forensic Inspector - Headers & Auth (Tab 2)
        # -------------------------------------------------------------
        print("[9/16] Capturing 09_forensic_headers_auth.png...")
        headers_tab = page.locator("button:has-text('Headers & Auth')").first
        if headers_tab.count() > 0:
            headers_tab.click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "09_forensic_headers_auth.png"))

        # -------------------------------------------------------------
        # 10. Forensic Inspector - Static URLs (Tab 3)
        # -------------------------------------------------------------
        print("[10/16] Capturing 10_forensic_static_urls.png...")
        urls_tab = page.locator("button:has-text('Static URLs')").first
        if urls_tab.count() > 0:
            urls_tab.click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "10_forensic_static_urls.png"))

        # -------------------------------------------------------------
        # 11. Forensic Inspector - Social Engineering (Tab 4)
        # -------------------------------------------------------------
        print("[11/16] Capturing 11_forensic_social_engineering.png...")
        social_tab = page.locator("button:has-text('Social Engineering')").first
        if social_tab.count() > 0:
            social_tab.click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "11_forensic_social_engineering.png"))

        # -------------------------------------------------------------
        # 12. Forensic Inspector - Raw RFC-822 Source (Tab 6)
        # -------------------------------------------------------------
        print("[12/16] Capturing 12_forensic_raw_mime_source.png...")
        raw_tab = page.locator("button:has-text('Raw RFC-822 Source')").first
        if raw_tab.count() > 0:
            raw_tab.click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "12_forensic_raw_mime_source.png"))

        # -------------------------------------------------------------
        # 13. Module A: Stylometric Authorship Card
        # -------------------------------------------------------------
        print("[13/16] Capturing 13_module_a_authorship_card.png...")
        author_card = page.locator("h3:has-text('AI Authorship Synthesizer')").first
        if author_card.count() > 0:
            author_card.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUTPUT_DIR / "13_module_a_authorship_card.png"))

        # -------------------------------------------------------------
        # 14. Legitimate / Benign Email Triage Result
        # -------------------------------------------------------------
        print("[14/16] Capturing 14_legitimate_email_result.png...")
        # Return to workspace
        return_btn = page.locator("button:has-text('Return to Workspace'), button:has-text('New Triage')").first
        if return_btn.count() > 0:
            return_btn.click()
            page.wait_for_timeout(800)
            # Select benign preset (Cloud Architecture Digest or Benefits)
            benign_preset = page.locator("div:has-text('Cloud Architecture Digest')").first
            if benign_preset.count() > 0:
                benign_preset.click()
                page.wait_for_timeout(400)
                # Analyze
                page.locator("button:has-text('Execute Risk Analysis')").first.click()
                page.wait_for_selector("text=Incident ID", timeout=15000)
                page.wait_for_timeout(1500)
                page.screenshot(path=str(OUTPUT_DIR / "14_legitimate_email_result.png"))

        # -------------------------------------------------------------
        # 15. Investigation Ledger Tab
        # -------------------------------------------------------------
        print("[15/16] Capturing 15_investigation_ledger.png...")
        ledger_nav = page.locator("button:has-text('Investigation Ledger')").first
        if ledger_nav.count() > 0:
            ledger_nav.click()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(OUTPUT_DIR / "15_investigation_ledger.png"))

        # -------------------------------------------------------------
        # 16. Research & Telemetry Tab
        # -------------------------------------------------------------
        print("[16/16] Capturing 16_research_telemetry.png...")
        telemetry_nav = page.locator("button:has-text('Research & Telemetry')").first
        if telemetry_nav.count() > 0:
            telemetry_nav.click()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUTPUT_DIR / "16_research_telemetry.png"))

        browser.close()
        print("\n[SUCCESS] All 16 process operation screenshots captured successfully!")

if __name__ == "__main__":
    capture_all_screenshots()
