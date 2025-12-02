import json
from bs4 import BeautifulSoup
import re

def get_ui_summary(html, logger, section_context=None):
    """
    Parses HTML to extract a structured summary of interactive elements.
    If section_context is provided, it narrows the search to that part of the page.
    """
    soup = BeautifulSoup(html, 'html.parser')
    search_area = soup

    # --- THIS IS THE FIX ---
    if section_context:
        # Find the element *containing* the section text
        text_tag = soup.find(lambda tag: tag.name not in ['script', 'style'] and section_context in tag.get_text(strip=True))

        if text_tag:
            # Now, find the closest parent container (div, form, fieldset, or section)
            # This ensures we search *around* the text, not just *inside* it.
            container = text_tag.find_parent(['div', 'form', 'fieldset', 'section'])
            if container:
                search_area = container  # Success! We will now *only* search inside this container.
                logger.info(f"Narrowed search to section: '{section_context}'")
            else:
                logger.warning(f"Could not find a parent container for section '{section_context}'. Searching whole page.")
        else:
            logger.warning(f"Could not find section text '{section_context}'. Searching whole page.")
    # --- END OF FIX ---

    interactive_elements = []

    # Find all potentially interactive elements *within the search_area*
    for element in search_area.find_all(['input', 'button', 'a', 'select', 'textarea']):
        selector = ''
        text = element.get_text(strip=True)

        # Prioritize selectors for stability
        if element.get('id'):
            selector = f"#{element.get('id')}"
        elif element.get('automation_id'):
            selector = f"[automation_id='{element.get('automation_id')}']"
        elif element.get('name'):
            selector = f"[name='{element.get('name')}']"

        # --- NEW FALLBACK ---
        # If no other selector is found, use the text
        elif text:
            # Create a Playwright-style text selector
            # We must escape quotes inside the text
            selector = f"text={json.dumps(text)}"
        # --- END OF NEW FALLBACK ---

        else:
            # Skip elements that cannot be reliably selected at all
            continue

        element_details = {
            "selector": selector,
            "text": text,
            "placeholder": element.get('placeholder', ''),
            "value": element.get('value', '')
        }
        interactive_elements.append(element_details)

    return json.dumps(interactive_elements, indent=2)


def build_prompt_for_step(ui_summary, current_step, last_error):
    """
    Builds a focused prompt for the agent to execute a single, specific step.
    """
    error_context = f'CRITICAL: YOUR LAST ATTEMPT FAILED! Error: "{last_error}". You MUST choose a different action or selector.' if last_error else ""
    action = current_step['action']

    section_instruction = ""
    if current_step.get("section"):
        section_instruction = f"You are working inside the '{current_step['section']}' section of the page."

    if action == 'fill':
        # --- FIX for KeyError ---
        # Changed 'field_name' to 'target_name' to match the parser's output
        field_name = current_step['target_name']
        # --- END OF FIX ---
        value = current_step['value']
        task_instructions = f"Your goal is to fill the field best described as '{field_name}' with the value '{value}'. Find the correct input element in the Current View and provide the 'fill' action."
    elif action == 'click':
        target_name = current_step['target_name']
        task_instructions = f"Your goal is to click the button or link best described as '{target_name}'. Find the correct element in the Current View and provide the 'click' action."
    elif action == 'click_first_in_list':
        list_name = current_step['list_name']
        task_instructions = f"Your goal is to click the FIRST clickable item (like a link or button) inside the list or container described as '{list_name}'. Find the correct element in the Current View and provide the 'click' action for it."
    else:
        # If the action is unknown (like 'wait'), return None.
        # This is handled by the test script, not the AI.
        return None

    return f"""
You are a meticulous test automation agent. Your task is to perform ONE specific action based on the current goal.
{section_instruction}
{error_context}
**Current Goal:** {task_instructions}
**Current View (Visible Interactive Elements):**
```json
{ui_summary}
```
**MANDATORY RESPONSE FORMAT:**
A single JSON object.
For a fill action: {{"action": "fill", "selector": "<css_selector>", "value": "<value>"}}
For a click action: {{"action": "click", "selector": "<css_selector>"}}
"""

def get_next_action_for_step(client, page, current_step, logger, last_error=""):
    """
    Gets the next single action from the AI for a specific, isolated step.
    """
    html = page.content()
    # --- THIS IS THE FIX ---
    # Pass the logger object to get_ui_summary so it can log warnings
    ui_summary = get_ui_summary(html, logger, section_context=current_step.get("section"))
    # --- END OF FIX ---

    prompt = build_prompt_for_step(ui_summary, current_step, last_error)

    if prompt is None:
        logger.warning(f"Could not build a prompt for the step action: {current_step.get('action')}")
        return None

    logger.info(f"Getting AI action for step: {current_step}")
    try:
        if hasattr(client, 'generate_content'):
            response = client.generate_content(prompt)
            response_text = response.text
        else:
            # Fallback for OpenAI-like client
            response = client.chat.completions.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}])
            response_text = response.choices[0].message.content

        match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        json_str = match.group(1) if match else response_text

        if not json_str.strip():
            logger.warning("AI returned an empty response.")
            return None

        action = json.loads(json_str)

        # --- Add validation for the AI's response ---
        if not isinstance(action, dict) or "action" not in action or "selector" not in action:
            logger.warning(f"AI returned invalid JSON: {json_str}")
            return None

        return action

    except Exception as e:
        logger.error(f"Failed to get or parse AI action for step {current_step}: {e}")
        return None