import sys
import time
from playwright.sync_api import sync_playwright

# This script will write its progress to a file named 'debug_log.txt'
with open("debug_log.txt", "w") as log_file:
    def log(message):
        # Print to console and write to the log file
        print(message)
        log_file.write(f"{time.time()}: {message}\n")
        log_file.flush() # Ensure data is written immediately

    log("STEP 1: Script started.")
    log(f"Python Version: {sys.version}")

    try:
        log("STEP 2: Entering sync_playwright context manager...")
        with sync_playwright() as p:
            log("STEP 3: Playwright context manager active.")
            log("STEP 4: Attempting to launch browser with a 30-second timeout...")

            # This is the line that launches the browser
            browser = p.chromium.launch(
                headless=False,
                slow_mo=500,
                timeout=30000,
                args=["--no-sandbox"]  # <-- Add this line
            )

            log("STEP 5: Browser launched successfully!")
            page = browser.new_page()
            page.goto("http://whatsmyuseragent.org/")
            log("STEP 6: Navigated to test page.")
            time.sleep(5)
            browser.close()
            log("STEP 7: Browser closed.")

    except Exception as e:
        log("\n--- AN ERROR OCCURRED ---")
        log(f"Error Type: {type(e).__name__}")
        log(f"Error Details: {e}")
        log("--------------------------")

    log("STEP 8: Script finished.")