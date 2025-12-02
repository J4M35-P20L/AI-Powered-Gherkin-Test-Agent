import pytest
import time
import os
from autotester.utils.workflow_memory import WorkflowMemory
from autotester.core.agent import get_ui_summary
from autotester.utils.env_loader import load_base_url
from playwright.sync_api import expect

def get_anomaly_description(client, baseline_summary, current_summary, logger):
    """Analyzes the difference between two UI summaries."""
    logger.info("Anomaly detected. Asking AI to describe the difference...")
    if '{"error":' in baseline_summary:
        return "The application transitioned to a completely new and unexpected page state."
    anomaly_prompt = f"""
As a QA Analyst, compare two UI summaries.
BASELINE:
{baseline_summary}
CURRENT:
{current_summary}

List the key breaking changes or anomalies.
"""
    try:
        if hasattr(client, 'generate_content'):
            response = client.generate_content(anomaly_prompt)
            return response.text
        else:
            return "Could not get anomaly description from AI."
    except Exception as e:
        logger.error(f"Failed to get anomaly description from AI: {e}")
        return "Could not get anomaly description from AI."


@pytest.mark.validation
def test_validate_workflow_for_current_url(page, logger, client):
    """
    This test loads the workflow for the BASE_URL and validates it step-by-step
    with a robust while loop and corrected state management logic.
    """
    base_url = load_base_url()
    app_name = WorkflowMemory.get_app_name_from_url(base_url)

    logger.info(f"--- Starting Workflow Validation for App: '{app_name}' ---")

    memory = WorkflowMemory(app_name=app_name)
    if not memory.graph or not memory.graph.get('edges'):
        pytest.fail(f"Workflow graph for '{app_name}' is empty. Please run the learning test first.")

    current_state_hash = "START"
    logger.info("Starting validation from the 'START' state.")

    # Safety measure to prevent any potential infinite loops during debugging.
    max_steps = 100
    step_count = 0

    while step_count < max_steps:
        step_count += 1

        # Find the next step in the workflow based on the current state
        next_edge = next((edge for edge in memory.graph['edges'] if edge.get('from') == current_state_hash), None)

        # If no next step is found, we have successfully reached the end of the path
        if not next_edge:
            logger.info("Reached the end of the learned path. Validation successful.")
            break

        action_to_perform = next_edge['action']
        expected_next_state_hash = next_edge['to']

        # Handle the initial page load state
        if action_to_perform.get('action') == 'initial_load':
            actual_initial_hash = memory.get_state_hash(page)
            if actual_initial_hash != expected_next_state_hash:
                pytest.fail(f"Initial page state does not match. Expected {expected_next_state_hash} but got {actual_initial_hash}.")

            logger.info(f"Initial page state matches: {actual_initial_hash}")
            current_state_hash = expected_next_state_hash
            continue

        logger.info(f"--- Executing Step: {action_to_perform} ---")
        try:
            action_type = action_to_perform.get('action')
            selector = action_to_perform.get('selector')

            if action_type == 'click':
                # FIX: Use page.expect_navigation() to correctly wait for page loads after a click.
                with page.expect_navigation(wait_until="networkidle", timeout=10000):
                    page.click(selector, timeout=5000)

            elif action_type == 'fill':
                # For fill actions, perform the action and then wait
                page.fill(selector, action_to_perform.get('value', ''), timeout=5000)
                # CRITICAL: Wait for the DOM to update after filling the field
                page.wait_for_timeout(500)

            logger.info("   Action executed successfully.")
        except Exception as e:
            pytest.fail(f"Could not execute action '{action_to_perform}'. Error: {e}")

        # Verify that the new state matches the expected state from the graph
        new_state_hash = memory.get_state_hash(page)
        if new_state_hash != expected_next_state_hash:
            pytest.fail(f"State mismatch after action. Expected {expected_next_state_hash} but got {new_state_hash}.")

        logger.info(f"State after action is correct: {new_state_hash}")

        # Update the current state to proceed to the next step in the loop
        current_state_hash = new_state_hash

    # Check if the loop terminated because it hit the max_steps limit
    if step_count >= max_steps:
        pytest.fail(f"Validation failed: Exceeded maximum steps ({max_steps}). The test is likely stuck in a loop.")

    logger.info(f"--- Workflow Validation Test Finished for '{app_name}' ---")

