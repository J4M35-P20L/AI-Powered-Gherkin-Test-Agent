import sys
from openai import OpenAI
from src.autotester.utils.logger import get_logger
from src.autotester.utils.env_loader import load_api_key
from src.autotester.core.feature_parser import parse_feature_file
from src.autotester.runner.playwright_runner import run_test_scenario

def main():
    logger = get_logger()
    try:
        api_key = load_api_key()
        client = OpenAI(api_key=api_key)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)

    try:
        test_input = input("Enter feature path and scenario (e.g., features/login.feature::Valid login): ")
        feature_path, scenario_name = test_input.split("::", 1)

        url, field_values, goal = parse_feature_file(feature_path, scenario_name)

        if not url:
            logger.error("Could not parse URL from feature file.")
            sys.exit(1)

        run_test_scenario(client, url, field_values, goal, logger)

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Error processing input: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()