import re

def parse_feature_file_to_steps(feature_path, target_scenario):
    """
    Parses a .feature file for a specific scenario and extracts Gherkin steps,
    including section context and direct selector steps.
    """
    steps = []
    in_scenario = False
    current_section = None

    # --- REGEX PATTERNS ---

    # --- NEW: Steps that provide their own selector ---
    fill_by_selector_pattern = re.compile(
        r'(?:When|And|Then)\s+I\s+enter\s+"(.*?)"\s+into\s+field\s+with\s+selector\s+"(.*?)"',
        re.IGNORECASE
    )
    click_by_selector_pattern = re.compile(
        r'(?:When|And|Then)\s+I\s+click\s+element\s+with\s+selector\s+"(.*?)"',
        re.IGNORECASE
    )

    # --- Standard AI-driven steps ---
    fill_pattern_1 = re.compile(r'(?:When|And|Then)\s+I\s+enter\s+(.+?)\s+as\s+"(.*?)"', re.IGNORECASE)
    fill_pattern_2 = re.compile(r'(?:When|And|Then)\s+I\s+enter\s+"(.*?)"\s+as\s+(.*)', re.IGNORECASE)
    click_pattern_quoted = re.compile(r'(?:When|And|Then)\s+I\s+click\s+on\s+"(.*?)"(?: \s+button)?', re.IGNORECASE)
    click_pattern_unquoted = re.compile(r'(?:When|And|Then)\s+I\s+click\s+on\s+([^\"]*)', re.IGNORECASE)

    # --- Context and Wait steps ---
    wait_pattern = re.compile(
        r'(?:When|And|Then)\s+I\s+(?:should be on the|see the|see|wait for)\s+"(.*?)"(?: \s+page)?', re.IGNORECASE
    )
    section_pattern = re.compile(r'(?:Given|And|When)\s+I\s+am\s+under\s+the\s+"(.*?)"\s+section', re.IGNORECASE)


    with open(feature_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.strip()

            if stripped_line.startswith(f"Scenario: {target_scenario}"):
                in_scenario = True
                continue

            if in_scenario:
                if stripped_line.startswith('Scenario:') or (not stripped_line and steps):
                    break

                if not stripped_line or stripped_line.startswith('#'):
                    continue

                # Skip any "Given" step that isn't a section step
                if stripped_line.lower().startswith("given") and not section_pattern.match(stripped_line):
                    continue

                # --- PARSING LOGIC ---

                # Check for "By Selector" steps FIRST
                fill_sel_match = fill_by_selector_pattern.match(stripped_line)
                if fill_sel_match:
                    value = fill_sel_match.group(1).strip()
                    selector = fill_sel_match.group(2).strip()
                    steps.append({'action': 'fill', 'selector': selector, 'value': value})
                    continue

                click_sel_match = click_by_selector_pattern.match(stripped_line)
                if click_sel_match:
                    selector = click_sel_match.group(1).strip()
                    steps.append({'action': 'click', 'selector': selector})
                    continue

                # --- Standard AI-driven steps ---
                section_match = section_pattern.match(stripped_line)
                if section_match:
                    current_section = section_match.group(1).strip()
                    continue

                fill_match_1 = fill_pattern_1.match(stripped_line)
                if fill_match_1:
                    target_name = fill_match_1.group(1).strip()
                    value = fill_match_1.group(2).strip()
                    steps.append({'action': 'fill', 'target_name': target_name, 'value': value, 'section': current_section})
                    continue

                fill_match_2 = fill_pattern_2.match(stripped_line)
                if fill_match_2:
                    value = fill_match_2.group(1).strip()
                    target_name = fill_match_2.group(2).strip()
                    steps.append({'action': 'fill', 'target_name': target_name, 'value': value, 'section': current_section})
                    continue

                click_match_q = click_pattern_quoted.match(stripped_line)
                if click_match_q:
                    target_name = click_match_q.group(1).strip()
                    steps.append({'action': 'click', 'target_name': target_name, 'section': current_section})
                    continue

                click_match_u = click_pattern_unquoted.match(stripped_line)
                if click_match_u:
                    target_name = click_match_u.group(1).strip().replace('button', '').strip()
                    if target_name:
                        steps.append({'action': 'click', 'target_name': target_name, 'section': current_section})
                        continue

                wait_match = wait_pattern.match(stripped_line)
                if wait_match:
                    target_name = wait_match.group(1).strip()
                    steps.append({'action': 'wait', 'target_name': target_name})
                    current_section = None # Reset section after a wait
                    continue

    return steps