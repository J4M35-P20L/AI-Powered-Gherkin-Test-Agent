import re

def parse_feature_file(feature_path, scenario_name):
    url, field_map, goal = None, {}, "Achieve the final objective."
    with open(feature_path, "r") as file:
        content = file.read()

    scenario_regex = re.compile(f"Scenario: {re.escape(scenario_name)}.*?((?=Scenario:)|$)", re.S)
    match = scenario_regex.search(content)

    if not match:
        return None, {}, ""

    scenario_block = match.group(0)

    url_match = re.search(r'Given I am on the website "([^"]+)"', scenario_block, re.I)
    if url_match:
        url = url_match.group(1)

    for m in re.finditer(r'When I enter "([^"]+)" as "([^"]+)"', scenario_block, re.I):
        field_map[m.group(1).strip()] = m.group(2).strip()

    goal_match = re.search(r'Then I should "([^"]+)"', scenario_block, re.I)
    if goal_match:
        goal = goal_match.group(1)

    return url, field_map, goal