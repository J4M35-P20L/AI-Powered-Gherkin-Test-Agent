import pytest
import time
import os
from autotester.core.agent import get_next_action_for_step
from autotester.core.feature_parser import parse_feature_file_to_steps
from playwright.sync_api import expect

def find_all_scenarios():
    """Finds all scenarios in the .feature files."""
    scenarios = []
    features_dir = 'features'
    if not os.path.isdir(features_dir):
        return []

    for filename in os.listdir(features_dir):
        if filename.endswith('.feature'):
            filepath = os.path.join(features_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            for line in content.splitlines():
                if line.strip().startswith('Scenario:'):
                    scenario_name = line.replace('Scenario:', '').strip()
                    test_id = f"Run_{filename}::{scenario_name}"
                    scenarios.append(pytest.param(filepath, scenario_name, id=test_id))
    return scenarios

@pytest.mark.scenario
@pytest.mark.parametrize("feature_path, scenario_name", find_all_scenarios())
def test_feature_scenario(feature_path, scenario_name, page, logger, client):
    """
    Runs a specific scenario from a feature file for direct execution.
    """
    logger.info(f"--- Starting Scenario: {scenario_name} ---")

    parsed_steps = parse_feature_file_to_steps(feature_path, scenario_name)
    if not parsed_steps:
        pytest.fail(f"Could not parse any steps for scenario '{scenario_name}'")

    last_error = ""

    for step in parsed_steps:
        logger.info(f"--- Executing Step: {step} ---")

        if step['action'] == 'wait':
            try:
                target_element = page.get_by_text(step['target_name'], exact=False)
                expect(target_element.first).to_be_visible(timeout=15000)
            except Exception as e:
                pytest.fail(f"Wait action failed. Error: {e}")
            continue

        # --- THIS IS THE FIX ---
        # Check if the parser already gave us a selector
        if step.get('selector'):
            logger.info("Selector provided in step, skipping AI call.")
            action_to_perform = step  # Use the step directly
        else:
            # No selector provided, call the AI
            action_to_perform = get_next_action_for_step(client, page, step, logger, last_error)
            last_error = ""

            if not action_to_perform:
                pytest.fail(f"AI failed to provide an action for step: {step}.")
        # --- END OF FIX ---

        try:
            action_type = action_to_perform.get('action')
            selector = action_to_perform.get('selector')

            if action_type == 'click':
                page.click(selector, timeout=5000)

            elif action_type == 'fill':
                page.fill(selector, action_to_perform.get('value', ''), timeout=5000)

            page.wait_for_timeout(500)

            logger.info(f"   Action '{action_type}' on '{selector}' executed successfully.")

        except Exception as e:
            pytest.fail(f"Action {action_to_perform} failed for step {step}: {e}")

        time.sleep(1)

    logger.info(f"--- Scenario {scenario_name} Completed ---")