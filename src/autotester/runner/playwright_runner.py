import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from src.autotester.core.agent import get_next_actions

def run_test_scenario(client, url, field_values, initial_goal, logger):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state('domcontentloaded')
        except PlaywrightTimeoutError:
            logger.error(f"Timeout error while loading the initial URL: {url}")
            browser.close()
            return

        max_steps = 10
        step = 0
        remaining_fields = field_values.copy()
        last_error = ""

        # Main loop to fill in all the fields
        while step < max_steps and remaining_fields:
            logger.info(f"--- Step {step + 1}/{max_steps} ---")
            logger.info(f"Fields remaining to fill: {list(remaining_fields.keys())}")

            actions = get_next_actions(client, page, remaining_fields, initial_goal, logger, last_error)
            last_error = ""

            if not actions:
                logger.warning("Agent returned no actions. Ending step.")
                step += 1
                continue

            successful_actions = []
            for action in actions:
                if not all(key in action for key in ["action", "selector", "value"]):
                    logger.error(f"Agent returned an invalid action object, skipping: {action}")
                    continue

                logger.info(f"-> Attempting: {action}")
                try:
                    action_type = action['action']
                    if action_type == 'click':
                        page.click(action['selector'], timeout=5000)
                    elif action_type == 'fill':
                        page.fill(action['selector'], action['value'], timeout=5000)

                    logger.info("   Success!")
                    successful_actions.append(action)

                except Exception as e:
                    error_message = f"Action \"{action['action']}\" on selector \"{action['selector']}\" failed. Playwright error: {str(e).splitlines()[0]}"
                    logger.error(error_message)
                    last_error += error_message + "\n"

            for action in successful_actions:
                if action['action'] == 'fill':
                    key_to_remove = next((key for key, value in remaining_fields.items() if value == action['value']), None)
                    if key_to_remove:
                        del remaining_fields[key_to_remove]
                        logger.info(f"Successfully filled '{key_to_remove}'.")

            step += 1
            time.sleep(1.5)

        # CORRECTED FINAL ACTION BLOCK
        if not remaining_fields:
            logger.info("All fields have been filled. Performing final action.")
            # Give the AI a simple, direct goal for the final step.
            final_goal = "Click the final login/submit button."
            final_actions = get_next_actions(client, page, {}, final_goal, logger, "")
            if final_actions:
                for action in final_actions:
                    logger.info(f"-> Attempting final action: {action}")
                    try:
                        page.click(action['selector'], timeout=5000)
                        logger.info("   Final action successful!")
                    except Exception as e:
                        logger.error(f"Final action failed: {e}")
            else:
                logger.warning("AI did not provide a final action.")
        else:
            logger.warning(f"Test finished, but some fields were not filled: {list(remaining_fields.keys())}")

        logger.info("Test finished.")
        time.sleep(3)
        browser.close()