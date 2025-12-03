# AI-Powered Web & Desktop Testing Framework

An intelligent, hybrid test automation framework that uses Google Gemini AI to translate human-readable Gherkin scenarios into executable Playwright (Web) and Pywinauto (Desktop) actions.

Unlike traditional frameworks with brittle selectors, this tool "sees" the UI, understands your intent, and dynamically interacts with applications.

# 🚀 Key Features

🤖 AI-Driven Execution: No hardcoded XPaths or CSS selectors. The AI analyzes the DOM or Window Tree to find elements based on semantic descriptions (e.g., "Click the Sign In button").

📝 Natural Language Tests: Write tests in simple Gherkin syntax (.feature files).

🧠 Self-Learning Mode: The framework "learns" applications by mapping workflows and saving robust selectors to a knowledge graph.

🛡️ Validation & Anomaly Detection: Replays learned workflows to detect regressions, UI changes, or anomalies in the application state.

💻 Hybrid Support: Supports both Web (Playwright) and Desktop (Pywinauto) automation in a single unified architecture.

# 📂 Project Structure
```
ai_test_gemini_framework/
├── features/                 # Gherkin feature files (Test Cases)
│   ├── amazon.feature
│   └── calculator.feature
├── src/
│   └── autotester/
│       ├── core/
│       │   ├── agent.py      # The AI Brain (Gemini Integration)
│       │   └── feature_parser.py
│       └── utils/
│           └── workflow_memory.py # Stores learned states/selectors
├── tests/
│   ├── test_scenarios.py     # Mode 1: AI Direct Execution
│   ├── test_learn_application.py # Mode 2: Learning/Training
│   ├── test_validation.py    # Mode 3: Validation/Regression
│   └── test_desktop_scenarios.py # Desktop Automation
├── conftest.py               # Pytest fixtures (Browser/App setup)
└── requirements.txt
```

# 🛠️ Setup & Installation

Clone the Repository:
```
git clone [https://github.com/your-username/ai-test-framework.git](https://github.com/your-username/ai-test-framework.git)
cd ai-test-framework
```

Create a Virtual Environment:
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

Install Dependencies:
```
pip install -r requirements.txt
playwright install
```

Configure Environment Variables: Create a .env file in the root directory:
```
# Get your key from aistudio.google.com
GEMINI_API_KEY=your_actual_api_key_here
BASE_URL=[https://www.amazon.com](https://www.amazon.com)
```

# 📝 Writing Tests (Gherkin)

Create .feature files in the features/ folder. The framework supports standard Gherkin syntax.

Example: **features/amazon.feature**
```
Feature: Basic User Workflow on Amazon

  @smoke @login
  Scenario Outline: Successful user login with valid credentials
    Given the user is on the Amazon homepage
    When the user navigates to the Sign In page
    And the user enters "<email>" in the email field
    And the user enters "<password>" in the password field
    And the user clicks the "Continue" button
    And the user clicks the "Sign In" button
    Then the user should see the "Hello, <username>" message on the navigation bar

    Examples:
      | email              | password       | username |
      | testuser@mail.com  | secure_pass123 | TestUser |
      | another_user@mail.com | mypass_2025 | Jane     |

  @search
  Scenario: Search for a specific product
    Given the user is logged in
    When the user enters "Mechanical Keyboard" in the search bar
    And the user clicks the "Search" button
    Then the user should see search results for "Mechanical Keyboard"
    And the product listing page title should contain "Mechanical Keyboard"
```

# 🏃‍♂️ Execution Modes

This framework operates in three distinct modes depending on your testing stage.

1. 🧠 Learning Mode (Training)

Goal: Explore the application, execute steps using AI, and build a "Workflow Memory" (workflow_graph.json).
When to use: When you have a new feature file or the UI has changed significantly.

The AI will:

Read your Gherkin step (e.g., "Click Login").

Analyze the page structure.

Determine the best selector.

Save the state transition and selector to the JSON graph.

Command:
```
# Run all learning tests
pytest tests/test_learn_application.py

# Run a specific feature file
pytest tests/test_learn_application.py -k "amazon"
```

2. 🛡️ Validation Mode (Regression)

Goal: Replay the learned workflow without calling the AI for every step.
When to use: CI/CD pipelines, nightly builds, or quick regression checks.

This mode is fast. It uses the cached selectors from workflow_graph.json. If the UI has changed and the cached selector fails, it raises an Anomaly.

Command:
```
pytest tests/test_validation.py
```

3. 🧪 Scenario Mode (Live AI Testing)

Goal: Execute tests directly using the AI in real-time without saving/loading memory.
When to use: Debugging new prompts, testing the AI's reasoning capabilities, or one-off test runs.

Command:
```
pytest tests/test_scenarios.py -k "Amazon"
```

🚨 Anomaly Detection

Anomaly detection is implicit in the Validation Mode.

Workflow Deviation: If the application flow diverges from the path stored in workflow_graph.json, the framework flags an anomaly.

UI Changes: If a stored selector no longer works, the framework catches the exception.

Reporting: (Future) The AI can be triggered upon failure to analyze the DOM and provide a root cause analysis (e.g., "The Login button ID changed from #submit to #btn-login").

🤝 Contributing

Fork the repository.

Create a feature branch (```git checkout -b feature/AmazingFeature```).

Commit your changes (```git commit -m 'Add some AmazingFeature'```).

Push to the branch (```git push origin feature/AmazingFeature```).

Open a Pull Request.

📄 License

Distributed under the MIT License.
