# AI-Powered Testing Framework

This project uses an AI agent to automate web browser testing based on Gherkin-style feature files.

## Project Structure

- `src/autotester/`: Main application source code.
    - `main.py`: Entry point to run the framework.
    - `core/`: Core AI logic and feature parsing.
    - `runner/`: Playwright browser automation logic.
    - `utils/`: Helper utilities for logging and environment management.
- `features/`: Contains the `.feature` files with test scenarios.
- `requirements.txt`: A list of Python dependencies.
- `.env`: (You must create this) For storing the `OPENAI_API_KEY`.

## How to Run

1.  **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    playwright install
    ```

2.  **Set Up Environment:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your_api_key_here"
    ```

3.  **Run a Test:**
    Execute the framework from the root directory:
    ```sh
    python -m src.autotester.main
    ```
    When prompted, enter the path to the test scenario, for example: `features/login.feature::Valid login`