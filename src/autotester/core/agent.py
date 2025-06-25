import json
from bs4 import BeautifulSoup
import re

def get_ui_summary(html):
    """
    Parses HTML to extract a structured summary of interactive elements
    and creates valid CSS selectors for Playwright.
    """
    soup = BeautifulSoup(html, 'html.parser')
    interactive_elements = []

    for element in soup.find_all(['input', 'button', 'a', 'select', 'textarea']):
        selector = ''
        if element.get('id'):
            selector = f"#{element.get('id')}"
        elif element.get('automation_id'):
            selector = f"[automation_id='{element.get('automation_id')}']"
        elif element.get('name'):
            selector = f"[name='{element.get('name')}']"

        if not selector:
            continue

        element_details = {
            "selector": selector,
            "text": element.get_text(strip=True),
            "placeholder": element.get('placeholder', '')
        }
        interactive_elements.append(element_details)

    return json.dumps(interactive_elements, indent=2)


def build_prompt(ui_summary, remaining_fields, goal, last_error):
    """
    Builds the most optimized prompt to reduce unnecessary retries and speed up execution.
    """
    field_instructions = "\n".join([f'- {k}: "{v}"' for k, v in remaining_fields.items()])

    error_context = ""
    if last_error:
        error_context = f"""
**CRITICAL: YOUR LAST ACTION FAILED!**
- **Error:** "{last_error}"
- **Analysis:** This error means the element you targeted was not visible or ready.
- **New Instruction:** DO NOT try the same action again. You MUST choose a different action. If you tried to fill a field and it failed, your only logical next step is to click a button that might make it visible.
---
"""

    task_instructions = f"""
**Your Step-by-Step Instructions:**
1.  **Analyze the UI:** Compare the "Data You Still Need to Enter" with the "Current View".
2.  **Fill Visible Fields (Priority 1):** If any fields you need to enter are visible in the Current View, your action is to "fill" them.
3.  **Click to Proceed (Priority 2):** If there are no visible fields to fill, but you still have data to enter (like a hidden password), you MUST click a button like 'Login' or 'Next' to proceed.
"""
    if not remaining_fields:
        task_instructions = """
**Your Task:**
All data has been entered. Your only job now is to click the final 'Login' or 'Submit' button to complete the goal.
"""

    return f"""
You are a fast and efficient test automation agent.
{error_context}
**Overall Goal:** "{goal}"

**Data You Still Need to Enter:**
{field_instructions if remaining_fields else "All data has been entered."}

**Current View (Visible Interactive Elements):**
```json
{ui_summary}
{task_instructions}

MANDATORY RESPONSE FORMAT:
A JSON array of action objects with "action", "selector", and "value" keys.
"""

def get_next_actions(client, page, remaining_fields, goal, logger, last_error=""):
    html = page.content()
    ui_summary = get_ui_summary(html)
    prompt = build_prompt(ui_summary, remaining_fields, goal, last_error)
    logger.info("Getting next actions from AI agent...")
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a web automation agent that only responds with a valid JSON array following strict formatting rules."},
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content

        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()

        if not response_text:
            logger.warning("AI returned an empty response.")
            return []
        actions = json.loads(response_text)
        return actions if isinstance(actions, list) else []
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from AI response: {response_text}")
        return []
    except Exception as e:
        logger.error(f"Error processing AI response: {e}")
        return []